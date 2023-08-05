from etsy.listing.views.listing import EtsyListingViewSet
from rest_framework.routers import DefaultRouter

app_name = "etsy.listing"


router = DefaultRouter()
router.register("", EtsyListingViewSet, basename="listing")


urlpatterns = router.urls
