import warnings

from django.db import IntegrityError
from django.core.urlresolvers import reverse, NoReverseMatch
from rest_framework.response import Response
from rest_framework import  serializers
from oscar.core.loading import get_class, get_model

from api.v1.utils import (
    OscarHyperlinkedModelSerializer,
    OscarModelSerializer,
    overridable
)
Country = get_model('address', 'Country')
UserAddress = get_model('address', 'UserAddress')

class CountrySerializer(OscarHyperlinkedModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class UserAddressSerializer(OscarModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='useraddress-detail')
    country = serializers.HyperlinkedRelatedField(
        view_name='country-detail', queryset=Country.objects)

    def create(self, validated_data):
        request = self.context['request']
        validated_data['user'] = request.user
        try:
            return super(UserAddressSerializer, self).create(validated_data)
        except IntegrityError as e:
            raise exceptions.NotAcceptable(str(e))

    def update(self, instance, validated_data):
        # to be sure that we cannot change the owner of an address. If you
        # want this, please override the serializer
        request = self.context['request']
        validated_data['user'] = request.user
        try:
            return super(
                UserAddressSerializer, self).update(instance, validated_data)
        except IntegrityError as e:
            raise exceptions.NotAcceptable(str(e))

    class Meta:
        model = UserAddress
        fields = overridable('OSCARAPI_USERADDRESS_FIELDS', (
            'id', 'title', 'first_name', 'last_name', 'line1', 'line2',
            'line3', 'line4', 'state', 'postcode', 'search_text',
            'phone_number', 'notes', 'is_default_for_shipping',
            'is_default_for_billing', 'country', 'url'))

