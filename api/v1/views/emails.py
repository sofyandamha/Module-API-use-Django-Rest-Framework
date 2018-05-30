from api.v1.permissions import IsOwner
from rest_framework import generics
from rest_framework.generics import ListAPIView

from api.v1 import serializers
from oscar.core.loading import get_model


Email = get_model('customer', 'Email')


__all__ = ('EmailHistoryList')

class EmailHistoryList(generics.ListAPIView):
    serializer_class = serializers.EmailSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        qs = Email.objects.all()
        return qs.filter(user=self.request.user)

