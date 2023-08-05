from ebay.listing.serializers.listing.base import BaseEbayListingSerializer
from rest_framework import serializers


class CreateEbayListingSerializer(BaseEbayListingSerializer):
    class Meta(BaseEbayListingSerializer.Meta):
        pass

    def validate(self, data):
        if self.Meta.model.objects.filter(
            channel=data["channel"], listing_sku=data["listing_sku"]
        ).exists():
            raise serializers.ValidationError("Листинг с таким SKU уже существует.")
        return super().validate(data)
