from ebay.category import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

app_name = "category"

# Create default router
router = DefaultRouter()

# Create routes for EbayCategoryViewSet
router.register(r"", views.EbayCategoryViewSet, basename="category")
category_aspect_router = NestedDefaultRouter(router, r"", lookup="category")
category_aspect_router.register(
    "aspect", views.EbayCategoryAspectViewSet, basename="category-aspect"
)

# Create urlpatterns
urlpatterns = router.urls
urlpatterns += category_aspect_router.urls
