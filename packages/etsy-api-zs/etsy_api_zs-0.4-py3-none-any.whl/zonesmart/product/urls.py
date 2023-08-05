from django.urls import path

from rest_framework.routers import DefaultRouter

from zonesmart.product import views

app_name = "zonesmart.base_product"

router = DefaultRouter()
router.register(r"product", views.BaseProductViewSet, basename="product")

urlpatterns = router.urls

urlpatterns += [path("images/<uuid:id>/", views.product_image_api_view, name="images")]
