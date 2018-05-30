import warnings

from django.db import IntegrityError
from rest_framework.response import Response

from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.translation import gettext as _
from oscar.core import prices
from oscar.core.loading import get_class, get_model
from rest_framework import exceptions, serializers

from api.v1.serializers.basket import (
    VoucherSerializer,
    OfferDiscountSerializer
)
from oscarapi.utils import (
    OscarHyperlinkedModelSerializer,
    OscarModelSerializer,
    overridable
)
from oscarapi.serializers.fields import TaxIncludedDecimalField

Country = get_model('address', 'Country')
ShippingAddress = get_model('order', 'ShippingAddress')
BillingAddress = get_model('order', 'BillingAddress')
Order = get_model('order', 'Order')
OrderLine = get_model('order', 'Line')
OrderLineAttribute = get_model('order', 'LineAttribute')

class InlineShippingAddressSerializer(OscarModelSerializer):
    country = serializers.HyperlinkedRelatedField(
        view_name='country-detail', queryset=Country.objects)

    class Meta:
        model = ShippingAddress
        fields = '__all__'


class BillingAddressSerializer(OscarHyperlinkedModelSerializer):
    class Meta:
        model = BillingAddress
        fields = '__all__'


class InlineBillingAddressSerializer(OscarModelSerializer):
    country = serializers.HyperlinkedRelatedField(
        view_name='country-detail', queryset=Country.objects)

    class Meta:
        model = BillingAddress
        fields = '__all__'

class OrderLineAttributeSerializer(OscarHyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='order-lineattributes-detail')

    class Meta:
        model = OrderLineAttribute
        fields = '__all__'


class OrderLineSerializer(OscarHyperlinkedModelSerializer):
    "This serializer renames some fields so they match up with the basket"

    url = serializers.HyperlinkedIdentityField(view_name='order-lines-detail')
    attributes = OrderLineAttributeSerializer(
        many=True, fields=('url', 'option', 'value'), required=False)
    price_currency = serializers.CharField(
        source='order.currency', max_length=12)
    price_excl_tax = serializers.DecimalField(
        decimal_places=2, max_digits=12, source='line_price_excl_tax')
    price_incl_tax = serializers.DecimalField(
        decimal_places=2, max_digits=12, source='line_price_incl_tax')
    price_incl_tax_excl_discounts = serializers.DecimalField(
        decimal_places=2, max_digits=12,
        source='line_price_before_discounts_incl_tax')
    price_excl_tax_excl_discounts = serializers.DecimalField(
        decimal_places=2, max_digits=12,
        source='line_price_before_discounts_excl_tax')

    class Meta:
        model = OrderLine
        fields = overridable('OSCAR_ORDERLINE_FIELD', default=[
            'attributes', 'url', 'product', 'stockrecord', 'quantity',
            'price_currency', 'price_excl_tax', 'price_incl_tax',
            'price_incl_tax_excl_discounts', 'price_excl_tax_excl_discounts',
            'order'])


class OrderOfferDiscountSerializer(OfferDiscountSerializer):
    name = serializers.CharField(source='offer_name')
    amount = serializers.DecimalField(decimal_places=2, max_digits=12)


class OrderVoucherOfferSerializer(OrderOfferDiscountSerializer):
    voucher = VoucherSerializer(required=False)


class OrderSerializer(OscarHyperlinkedModelSerializer):
    """
    The order serializer tries to have the same kind of structure as the
    basket. That way the same kind of logic can be used to display the order
    as the basket in the checkout process.
    """
    owner = serializers.HyperlinkedRelatedField(
        view_name='user-detail', read_only=True, source='user')
    lines = serializers.HyperlinkedIdentityField(
        view_name='order-lines-list')
    shipping_address = InlineShippingAddressSerializer(
        many=False, required=False)
    billing_address = InlineBillingAddressSerializer(
        many=False, required=False)

    payment_url = serializers.SerializerMethodField()
    offer_discounts = serializers.SerializerMethodField()
    voucher_discounts = serializers.SerializerMethodField()

    def get_offer_discounts(self, obj):
        qs = obj.basket_discounts.filter(offer_id__isnull=False)
        return OrderOfferDiscountSerializer(qs, many=True).data

    def get_voucher_discounts(self, obj):
        qs = obj.basket_discounts.filter(voucher_id__isnull=False)
        return OrderVoucherOfferSerializer(qs, many=True).data

    def get_payment_url(self, obj):
        try:
            return reverse('api-payment', args=(obj.pk,))
        except NoReverseMatch:
            msg = "You need to implement a view named 'api-payment' " \
                "which redirects to the payment provider and sets up the " \
                "callbacks."
            warnings.warn(msg)
            return msg

    class Meta:
        model = Order
        fields = overridable('OSCARAPI_ORDER_FIELD', default=(
            'number', 'basket', 'url', 'lines',
            'owner', 'billing_address', 'currency', 'total_incl_tax',
            'total_excl_tax', 'shipping_incl_tax', 'shipping_excl_tax',
            'shipping_address', 'shipping_method', 'shipping_code', 'status',
            'guest_email', 'date_placed', 'payment_url', 'offer_discounts',
            'voucher_discounts')
        )

class OrderOfferDiscountSerializer(OfferDiscountSerializer):
    name = serializers.CharField(source='offer_name')
    amount = serializers.DecimalField(decimal_places=2, max_digits=12)


class OrderVoucherOfferSerializer(OrderOfferDiscountSerializer):
    voucher = VoucherSerializer(required=False)