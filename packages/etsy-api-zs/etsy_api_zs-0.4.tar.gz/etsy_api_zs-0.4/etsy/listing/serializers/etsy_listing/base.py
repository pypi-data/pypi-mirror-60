from etsy.listing.models import EtsyListing
from rest_framework import serializers


class BaseEtsyListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtsyListing
        exclude = ["id"]
