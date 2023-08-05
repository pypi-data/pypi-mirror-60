from ebay.location.views import EbayLocationViewSet
from rest_framework.routers import DefaultRouter

app_name = "location"

router = DefaultRouter()
router.register("", EbayLocationViewSet, basename="location")

urlpatterns = router.urls
