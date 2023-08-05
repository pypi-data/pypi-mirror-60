from django_filters import filterset
from ebay.location.models import EbayLocation


class EbayLocationFilterSet(filterset.FilterSet):
    class Meta:
        model = EbayLocation
        fields = ["status"]
