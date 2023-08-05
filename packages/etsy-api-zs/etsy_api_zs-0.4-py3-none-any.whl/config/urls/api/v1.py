from django.urls import path, include


urlpatterns = [
    # Zone Smart API
    path("", include("zonesmart.urls", namespace="zonesmart")),
    # Ebay
    path("ebay/", include("ebay.urls", namespace="ebay")),
    # Amazon
    path("amazon/", include("amazon.urls", namespace="amazon")),
    # Etsy
    path("etsy/", include("etsy.urls", namespace="etsy")),
]
