from django.urls import include, path

app_name = "ebay"


urlpatterns = [
    path("account/", include("ebay.account.urls", namespace="account")),
    path("category/", include("ebay.category.urls", namespace="category")),
    path("listing/", include("ebay.listing.urls", namespace="listing")),
    path("policy/", include("ebay.policy.urls", namespace="policy")),
    path("location/", include("ebay.location.urls", namespace="location")),
    path("order/", include("ebay.order.urls", namespace="order")),
    path("negotiation/", include("ebay.negotiation.urls", namespace="negotiation")),
    path("notification/", include("ebay.notification.urls", namespace="notification")),
]
