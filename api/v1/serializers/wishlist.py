from rest_framework import serializers
from oscar.core.loading import get_model

ProductAlert = get_model('customer', 'ProductAlert')
WishList = get_model('wishlists', 'WishList')

class WishlistSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)


    class Meta:
        model = WishList
        fields = ('id', 'name')

    def create(self, validated_data):
        return WishList.objects.create(**validated_data)


class ProductAlertSerializer(serializers.Serializer):

    class Meta:
        model = ProductAlert
        fields = ('id', 'product_id', 'status', 'date_created')