from django_filters import rest_framework as filters
from ebay.listing.models import EbayListing


class EbayProductFilter(filters.FilterSet):
    class Meta:
        model = EbayListing
        fields = ["status"]
