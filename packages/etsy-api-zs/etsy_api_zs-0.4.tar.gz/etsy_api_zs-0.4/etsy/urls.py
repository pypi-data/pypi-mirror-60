from django.urls import include, path
from rest_framework.routers import DefaultRouter

from etsy.views import EtsyCountryViewSet, EtsyRegionViewSet

app_name = "etsy"


router = DefaultRouter()
router.register("country", EtsyCountryViewSet, basename="country")
router.register("region", EtsyRegionViewSet, basename="region")


urlpatterns = [
    path("account/", include("etsy.account.urls", namespace="account")),
    path("listing/", include("etsy.listing.urls", namespace="listing")),
    path("policy/", include("etsy.policy.urls", namespace="policy")),
]

urlpatterns += router.urls
