from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from oscar.core.loading import get_model
from api.v1.permissions import IsOwner
from api.v1 import serializers

ProductAlert = get_model('customer', 'ProductAlert')
WishList = get_model('wishlists', 'WishList')


__all__ = ('WishListView', 'WishListCreateAPIView', 
			'ProductAlertView')

class WishListView(generics.ListAPIView):
	queryset = WishList.objects.all()
	serializer_class = serializers.WishlistSerializer
	permission_classes = (IsOwner,)

	def get_queryset(self, pk=None):
		user = self.request.user
		return user.wishlists.all()

	def get(self, request, format=None):
		wishlists = self.get_queryset()
		serializer = serializers.WishlistSerializer(wishlists, many=True)
		return Response(serializer.data)



class WishListCreateAPIView(generics.CreateAPIView):
	queryset = WishList.objects.all()
	serializer_class = serializers.WishlistSerializer

	def get_object(self, pk):
		try:
			return WishList.objects.get(pk=pk)
		except WishList.DoesNotExist:
			raise Http404

	def get(self, request, pk, format=None):
		wishlists = self.get_object(pk)
		serializer = serializers.WishlistSerializer(wishlists)
		return Response(serializer.data)

	def put(self, request, pk, format=None):
		wishlists = self.get_object(pk)
		serializer = serializers.WishlistSerializer(wishlists, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk, format=None):
		wishlists = self.get_object(pk)
		wishlists.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)


class ProductAlertView(generics.ListAPIView):
	queryset = ProductAlert.objects.all()
	serializer_class = serializers.ProductAlertSerializer
	permission_classes = (IsOwner,)

	def get_queryset(self, pk=None):
		user = self.request.user
		return user.customer.select_related()

	def get(self, request, format=None):
		alerts = self.get_queryset()
		serializer = serializers.ProductAlertSerializer(alerts, many=True)
		return Response(serializer.data)