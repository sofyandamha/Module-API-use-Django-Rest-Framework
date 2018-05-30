from oscar.core.loading import get_model
from api.v1.permissions import IsOwner
from api.v1.serializers import (
     OrderLineAttributeSerializer, OrderLineSerializer,
    OrderSerializer
)
from rest_framework import generics, response, status, views

Order = get_model('order', 'Order')
OrderLine = get_model('order', 'Line')
OrderLineAttribute = get_model('order', 'LineAttribute')

__all__ = (
    'OrderList', 'OrderDetail',
    'OrderLineList', 'OrderLineDetail',
    'OrderLineAttributeDetail',
)


class OrderList(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        qs = Order.objects.all()
        return qs.filter(user=self.request.user)


class OrderDetail(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsOwner,)


class OrderLineList(generics.ListAPIView):
    queryset = OrderLine.objects.all()
    serializer_class = OrderLineSerializer

    def get(self, request, pk=None, format=None):
        if pk is not None:
            self.queryset = self.queryset.filter(
                order__id=pk, order__user=request.user)
        elif not request.user.is_staff:
            self.permission_denied(request)

        return super(OrderLineList, self).get(request, format)


class OrderLineDetail(generics.RetrieveAPIView):
    queryset = OrderLine.objects.all()
    serializer_class = OrderLineSerializer

    def get(self, request, pk=None, format=None):
        if not request.user.is_staff:
            self.queryset = self.queryset.filter(
                order__id=pk, order__user=request.user)

        return super(OrderLineDetail, self).get(request, format)


class OrderLineAttributeDetail(generics.RetrieveAPIView):
    queryset = OrderLineAttribute.objects.all()
    serializer_class = OrderLineAttributeSerializer