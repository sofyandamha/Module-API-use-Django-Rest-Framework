from api.v1.views.root import *
from api.v1.views.login import (
	ChangePasswordView,
	LoginView,
	UserProfileChangeAPIView )

from api.v1.views.category import *
from api.v1.views.addresses import *
from api.v1.views.product import *
from api.v1.views.orders import *
from api.v1.views.basket import *
from api.v1.views.emails import EmailHistoryList
from api.v1.views.wishlist import WishListView, WishListCreateAPIView, ProductAlertView