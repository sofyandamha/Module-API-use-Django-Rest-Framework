import warnings
from rest_framework import serializers
from rest_framework import generics
from oscar.core.loading import get_model

from api.v1.utils import (
    overridable,
    OscarModelSerializer
)
Email = get_model('customer', 'Email')

class EmailSerializer(OscarModelSerializer):
    subject = serializers.CharField(max_length=128)
    date_sent = serializers.CharField(max_length=128)

    class Meta:
        model = Email
        fields = overridable('OSCARAPI_EMAIL_FIELDS', (
            'id', 'subject', 'date_sent'))