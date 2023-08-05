from ebay.policy import views
from rest_framework.routers import DefaultRouter

app_name = "policy"

router = DefaultRouter()
router.register(r"fulfillment", views.FulfillmentPolicyViewSet, basename="fulfillment")
router.register(r"payment", views.PaymentPolicyViewSet, basename="payment")
router.register(r"return", views.ReturnPolicyViewSet, basename="return")

urlpatterns = router.urls
