from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import auth

from oscar.apps.basket import signals
from oscar.core.loading import get_model, get_class

from rest_framework import status, generics, exceptions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser

from api.v1 import serializers, permissions
from api.v1.basket import operations
from api.v1.views.mixin import PutIsPatchMixin
from api.v1.views.utils import BasketPermissionMixin

__all__ = ('BasketList', 'BasketDetail','BasketView', 'LineList', 'LineDetail', 'AddProductView',
           'BasketLineDetail', 'AddVoucherView', 'shipping_methods', 'UserList', 'UserDetail',)

Basket = get_model('basket', 'Basket')
Line = get_model('basket', 'Line')
Repository = get_class('shipping.repository', 'Repository')
User = auth.get_user_model()

class BasketView(APIView):
    serializer_class = serializers.BasketSerializer

    def get(self, request, format=None):
        basket = operations.get_basket(request)
        ser = self.serializer_class(basket, context={'request': request})
        return Response(ser.data)


class AddProductView(APIView):
    add_product_serializer_class = serializers.AddProductSerializer
    serializer_class = serializers.BasketSerializer

    def validate(self, basket, product, quantity, options):
        availability = basket.strategy.fetch_for_product(
            product).availability

        # check if product is available at all
        if not availability.is_available_to_buy:
            return False, availability.message

        # check if we can buy this quantity
        allowed, message = availability.is_purchase_permitted(quantity)
        if not allowed:
            return False, message

        # check if there is a limit on amount
        allowed, message = basket.is_quantity_allowed(quantity)
        if not allowed:
            return False, message
        return True, None

    def post(self, request, format=None):
        p_ser = self.add_product_serializer_class(
            data=request.data, context={'request': request})
        if p_ser.is_valid():
            basket = operations.get_basket(request)
            product = p_ser.validated_data['url']
            quantity = p_ser.validated_data['quantity']
            options = p_ser.validated_data.get('options', [])

            basket_valid, message = self.validate(
                basket, product, quantity, options)
            if not basket_valid:
                return Response(
                    {'reason': message},
                    status=status.HTTP_406_NOT_ACCEPTABLE)

            basket.add_product(product, quantity=quantity, options=options)
            operations.apply_offers(request, basket)
            ser = self.serializer_class(
                basket, context={'request': request})
            return Response(ser.data)

        return Response(
            {'reason': p_ser.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)


class AddVoucherView(APIView):
    add_voucher_serializer_class = serializers.VoucherAddSerializer
    serializer_class = serializers.VoucherSerializer

    def post(self, request, format=None):
        v_ser = self.add_voucher_serializer_class(
            data=request.data, context={'request': request})
        if v_ser.is_valid():
            basket = operations.get_basket(request)

            voucher = v_ser.instance
            basket.vouchers.add(voucher)

            signals.voucher_addition.send(
                sender=None, basket=basket, voucher=voucher)

            # Recalculate discounts to see if the voucher gives any
            operations.apply_offers(request, basket)
            discounts_after = basket.offer_applications

            # Look for discounts from this new voucher
            for discount in discounts_after:
                if discount['voucher'] and discount['voucher'] == voucher:
                    break
            else:
                basket.vouchers.remove(voucher)
                return Response(
                    {'reason': _(
                        "Your basket does not qualify for a voucher discount")},  # noqa
                    status=status.HTTP_406_NOT_ACCEPTABLE)

            ser = self.serializer_class(
                voucher, context={'request': request})
            return Response(ser.data)

        return Response(v_ser.errors, status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(('GET',))
def shipping_methods(request, format=None):
    basket = operations.get_basket(request)
    shiping_methods = Repository().get_shipping_methods(
        basket=basket, user=request.user,
        request=request)
    ser = serializers.ShippingMethodSerializer(
        shiping_methods, many=True, context={'basket': basket})
    return Response(ser.data)


class LineList(BasketPermissionMixin, generics.ListCreateAPIView):
    serializer_class = serializers.LineSerializer
    queryset = Line.objects.all()

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if pk is not None:  # usually we need the lines of the basket
            basket = self.check_basket_permission(self.request, basket_pk=pk)
            prepped_basket = operations.assign_basket_strategy(
                basket, self.request)
            return prepped_basket.all_lines()
        elif self.request.user.is_staff:  # admin users can view a bit more
            return super(LineList, self).get_queryset()
        else:  # non admin users can view nothing at all here.
            return self.permission_denied(self.request)

    def get(self, request, pk=None, format=None):
        if pk is not None:
            basket = self.check_basket_permission(request, pk)
            prepped_basket = operations.assign_basket_strategy(basket, request)
            self.queryset = prepped_basket.all_lines()
            self.serializer_class = serializers.BasketLineSerializer

        return super(LineList, self).get(request, format)

    def post(self, request, pk=None, format=None):
        data_basket = self.get_data_basket(request.data, format)
        self.check_basket_permission(request, basket=data_basket)

        if pk is not None:
            url_basket = self.check_basket_permission(request, basket_pk=pk)
            if url_basket != data_basket:
                raise exceptions.NotAcceptable(
                    _('Target basket inconsistent %s != %s') % (
                        url_basket.pk, data_basket.pk
                    )
                )
        elif not request.user.is_staff:
            self.permission_denied(request)

        return super(LineList, self).post(request, format=format)


class LineDetail(PutIsPatchMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Line.objects.all()
    serializer_class = serializers.LineSerializer
    permission_classes = (permissions.IsAdminUserOrRequestContainsLine,)

    def get(self, request, pk=None, format=None):
        line = self.get_object()
        basket = operations.get_basket(request)

        # if the line is from the current basket, use the serializer that
        # computes the prices by using the strategy.
        if line.basket == basket:
            operations.assign_basket_strategy(line.basket, request)
            ser = serializers.BasketLineSerializer(
                instance=line, context={'request': request})
            return Response(ser.data)

        return super(LineDetail, self).get(request, pk, format)


class BasketLineDetail(PutIsPatchMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Line.objects.all()
    serializer_class = serializers.BasketLineSerializer
    permission_classes = (permissions.IsAdminUserOrRequestContainsLine,)

    def get_queryset(self):
        basket_pk = self.kwargs.get('basket_pk')
        basket = get_object_or_404(operations.editable_baskets(), pk=basket_pk)
        prepped_basket = operations.prepare_basket(basket, self.request)
        if operations.request_contains_basket(self.request, prepped_basket):
            return prepped_basket.all_lines()
        else:
            return self.queryset.none()


class BasketList(generics.ListCreateAPIView):
    serializer_class = serializers.BasketSerializer
    queryset = Basket.objects.all()
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        qs = super(BasketList, self).get_queryset()
        return map(
            functools.partial(assign_basket_strategy, request=self.request),
            qs)


class BasketDetail(PutIsPatchMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.BasketSerializer
    permission_classes = (permissions.IsAdminUserOrRequestContainsBasket,)
    queryset = Basket.objects.all()

    def get_object(self):
        basket = super(BasketDetail, self).get_object()
        return assign_basket_strategy(basket, self.request)


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAdminUser,)


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAdminUser,)