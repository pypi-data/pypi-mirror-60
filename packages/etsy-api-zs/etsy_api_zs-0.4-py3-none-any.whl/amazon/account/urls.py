from amazon.account import views
from rest_framework.routers import DefaultRouter

app_name = "account"

router = DefaultRouter()
router.register(r"", views.AmazonUserAccountViewSet, basename="account")

urlpatterns = router.urls
