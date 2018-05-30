from oscar.core.loading import get_model
from api.v1.permissions import IsOwner
from api.v1.serializers import UserAddressSerializer, CountrySerializer
from rest_framework import generics

Country = get_model('address', 'Country')
UserAddress = get_model('address', 'UserAddress')

__all__ = (
    'UserAddressList',
    'UserAddressDetail',
    'CountryList',
    'CountryDetail',

)

class CountryList(generics.ListAPIView):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()

class CountryDetail(generics.RetrieveAPIView):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()

class UserAddressList(generics.ListCreateAPIView):
    serializer_class = UserAddressSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)


class UserAddressDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserAddressSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

