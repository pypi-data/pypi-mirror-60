from ebay.negotiation.views import EbayMessageViewSet
from rest_framework.routers import DefaultRouter

app_name = "ebay.negotiation"


router = DefaultRouter()


router.register(r"message", EbayMessageViewSet, basename="message")


urlpatterns = router.urls
