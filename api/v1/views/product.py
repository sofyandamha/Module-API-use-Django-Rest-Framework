from rest_framework import generics
from rest_framework.response import Response

from oscar.core.loading import get_class, get_model

from api.v1 import serializers


Selector = get_class('partner.strategy', 'Selector')

__all__ = (
    'ProductList', 'ProductDetail',
    'ProductPrice', 'ProductAvailability',
    'StockRecordList', 'StockRecordDetail',
)

Product = get_model('catalogue', 'Product')
StockRecord = get_model('partner', 'StockRecord')

class ProductList(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = serializers.ProductLinkSerializer

    def get_queryset(self):
        qs = super(ProductList, self).get_queryset()
        category = self.request.query_params.get('category')
        title = self.request.query_params.get('title')
        partner= self.request.query_params.get('partner')

        if category is not None:
            return qs.filter(categories__name=category)
        elif title is not None:
            return qs.filter(title__icontains=title)
            #Sekalian Search product Berdasarkan Mitra
        elif partner is not None:
            return qs.filter(stockrecords__partner__name=partner)
        return qs


class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer


class ProductPrice(generics.RetrieveAPIView):
    queryset = Product.objects.all()

    def get(self, request, pk=None, format=None):
        product = self.get_object()
        strategy = Selector().strategy(request=request, user=request.user)
        ser = serializers.PriceSerializer(
            strategy.fetch_for_product(product).price,
            context={'request': request})
        return Response(ser.data)


class ProductAvailability(generics.RetrieveAPIView):
    queryset = Product.objects.all()

    def get(self, request, pk=None, format=None):
        product = self.get_object()
        strategy = Selector().strategy(request=request, user=request.user)
        ser = serializers.AvailabilitySerializer(
            strategy.fetch_for_product(product).availability,
            context={'request': request})
        return Response(ser.data)

class StockRecordList(generics.ListAPIView):
    serializer_class = serializers.StockRecordSerializer
    queryset = StockRecord.objects.all()

    def get(self, request, pk=None, *args, **kwargs):
        if pk is not None:
            self.queryset = self.queryset.filter(product__id=pk)

        return super(StockRecordList, self).get(request, *args, **kwargs)


class StockRecordDetail(generics.RetrieveAPIView):
    queryset = StockRecord.objects.all()
    serializer_class = serializers.StockRecordSerializer
