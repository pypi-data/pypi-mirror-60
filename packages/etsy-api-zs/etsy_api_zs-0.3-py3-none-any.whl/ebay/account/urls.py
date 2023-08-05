from django.urls import path

from ebay.account import views
from ebay.account.views import EbayUserAccountAuthUrl
from rest_framework.routers import DefaultRouter

app_name = "account"


urlpatterns = [
    path("get_auth_url/", EbayUserAccountAuthUrl.as_view(), name="get_auth_url"),
]


router = DefaultRouter()
# router.register(r'rate_limits', views.EbayUserRateLimitsViewSet, basename='user_rate_limits')
router.register(r"", views.EbayUserAccountViewSet, basename="user_account")


urlpatterns += router.urls
