from ebay.listing.serializers.listing.base import BaseEbayListingSerializer


class UpdateEbayListingSerializer(BaseEbayListingSerializer):
    class Meta(BaseEbayListingSerializer.Meta):
        fields = [
            "category",
            "products",
            "aspects",
            "title",
            "compatibilities",
        ]

    def to_representation(self, instance):
        representation = BaseEbayListingSerializer(instance=instance).data
        return representation
