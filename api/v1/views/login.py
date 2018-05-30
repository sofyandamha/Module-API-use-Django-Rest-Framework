from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework import generics, mixins, permissions
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView, RetrieveAPIView

from oscar.core.loading import get_model
from api.v1 import serializers
from api.v1.utils import login_and_upgrade_session
from api.v1.basket import operations



__all__ = ('LoginView',)

Basket = get_model('basket', 'Basket')
User = get_user_model()

class LoginView(APIView):
    serializer_class = serializers.LoginSerializer

    def get(self, request, format=None):
        if settings.DEBUG:
            if request.user.is_authenticated():
                ser = serializers.UserSerializer(request.user, many=False)
                return Response(ser.data)
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise MethodNotAllowed('GET')

    def merge_baskets(self, anonymous_basket, basket):
        "Hook to enforce rules when merging baskets."
        basket.merge(anonymous_basket)

    def post(self, request, format=None):
        ser = self.serializer_class(data=request.data)
        if ser.is_valid():

            anonymous_basket = operations.get_anonymous_basket(request)

            user = ser.instance

            # refuse to login logged in users, to avoid attaching sessions to
            # multiple users at the same time.
            if request.user.is_authenticated():
                return Response(
                    {'detail': 'Session is in use, log out first'},
                    status=status.HTTP_405_METHOD_NOT_ALLOWED)

            request.user = user

            login_and_upgrade_session(request._request, user)

            # merge anonymous basket with authenticated basket.
            basket = operations.get_user_basket(user)
            if anonymous_basket is not None:
                self.merge_baskets(anonymous_basket, basket)

            operations.store_basket_in_session(basket, request.session)

            return Response(_("Welcome back"))

        return Response(ser.errors, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, format=None):
        request = request._request
        if request.user.is_anonymous():
            basket = operations.get_anonymous_basket(request)
            if basket:
                operations.flush_and_delete_basket(basket)

        request.session.clear()
        request.session.delete()
        request.session = None

        return Response("")

class ChangePasswordView(UpdateAPIView):
    serializer_class = serializers.ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # ini Cek Password lama 
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password juga menghapus password yang akan didapat pengguna
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(_("Password updated"), status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserProfileChangeAPIView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserProfileChangeSerializer

    def get_object(self):
        return self.request.user

    def put(self, request):
        obj = User.objects.get(id=request.user.id)
        serializer = serializers.UserProfileChangeSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
