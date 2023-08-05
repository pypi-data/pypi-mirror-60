from django.urls import include, path

app_name = "zonesmart"


urlpatterns = [
    path(
        "marketplace/", include("zonesmart.marketplace.urls", namespace="marketplace")
    ),
    path("news/", include("zonesmart.news.urls", namespace="news")),
    path("", include("zonesmart.support.urls", namespace="support")),
    path("", include("zonesmart.product.urls", namespace="base_product")),
]
