import django
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^$', views.api_root, name='api-root'),
    url(r'^basket/$', views.BasketView.as_view(), name='api-basket'),
    url(r'^basket/add-product/$', views.AddProductView.as_view(), name='api-basket-add-product'),
    url(r'^basket/add-voucher/$', views.AddVoucherView.as_view(), name='api-basket-add-voucher'),
    url(r'^basket/shipping-methods/$', views.shipping_methods, name='api-basket-shipping-methods'),
    url(r'^baskets/$', views.BasketList.as_view(), name='basket-list'),
    url(r'^baskets/(?P<pk>[0-9]+)/$', views.BasketDetail.as_view(), name='basket-detail'),
    url(r'^baskets/(?P<pk>[0-9]+)/lines/$', views.LineList.as_view(), name='basket-lines-list'),
    url(r'^baskets/(?P<basket_pk>[0-9]+)/lines/(?P<pk>[0-9]+)/$', views.BasketLineDetail.as_view(), name='basket-line-detail'),
    url(r'^categorys/$',views.CategoryList.as_view(), name='category-list'),
    url(r'^login/$', views.LoginView.as_view(), name='api-login'),
    url(r'^products/$', views.ProductList.as_view(), name='product-list'),
    url(r'^products/(?P<pk>[0-9]+)/$', views.ProductDetail.as_view(), name='product-detail'),
    url(r'^products/(?P<pk>[0-9]+)/price/$', views.ProductPrice.as_view(), name='product-price'),
    url(r'^products/(?P<pk>[0-9]+)/availability/$', views.ProductAvailability.as_view(), name='product-availability'),
    url(r'^products/(?P<pk>[0-9]+)/stockrecords/$', views.StockRecordList.as_view(), name='product-stockrecord-list'),
    url(r'^email/$', views.EmailHistoryList.as_view(), name='email-list'),
    url(r'^alert/$', views.ProductAlertView.as_view(), name='alerts'),
    url(r'^wishlist/$', views.WishListView.as_view(), name='wish-list'),
    url(r'^wishlist/add/$', views.WishListCreateAPIView.as_view(), name='create'),
    url(r'^users/$', views.UserList.as_view(), name='user-list'),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name='user-detail'),
    url(r'^useraddresses/$', views.UserAddressList.as_view(), name='useraddress-list'),
    url(r'^useraddresses/(?P<pk>[0-9]+)/$', views.UserAddressDetail.as_view(), name='useraddress-detail'),
    url(r'^countries/(?P<pk>[A-z]+)/$', views.CountryDetail.as_view(), name='country-detail'),
    url(r'^changepassword/$', views.ChangePasswordView.as_view(), name='api-changepassword'),
    url(r'^changeprofile/$', views.UserProfileChangeAPIView.as_view(), name='api-changeprofile'),
    url(r'^orders/$', views.OrderList.as_view(), name='order-list'),
    url(r'^orders/(?P<pk>[0-9]+)/$', views.OrderDetail.as_view(), name='order-detail'),
    url(r'^orders/(?P<pk>[0-9]+)/lines/$', views.OrderLineList.as_view(), name='order-lines-list'),
    url(r'^orderlines/(?P<pk>[0-9]+)/$', views.OrderLineDetail.as_view(), name='order-lines-detail'),
    url(r'^orderlineattributes/(?P<pk>[0-9]+)/$', views.OrderLineAttributeDetail.as_view(), name='order-lineattributes-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)

if django.VERSION[:2] < (1, 8):
    from django.conf.urls import patterns

    urlpatterns = patterns('', *urlpatterns)
