from django.urls import include, path

app_name = "amazon"

urlpatterns = [
    path("account/", include("amazon.account.urls", namespace="account")),
    path("order/", include("amazon.order.urls", namespace="order")),
]
