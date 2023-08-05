from amazon.order.views import AmazonOrderItemViewSet, AmazonOrderViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

app_name = "amazon.order"

router = DefaultRouter()

# Order router
router.register(r"", AmazonOrderViewSet, basename="order")
order_item_router = NestedDefaultRouter(router, r"", lookup="order")
order_item_router.register(r"item", AmazonOrderItemViewSet, basename="item")


urlpatterns = router.urls
# Add order item router urls
urlpatterns += order_item_router.urls
