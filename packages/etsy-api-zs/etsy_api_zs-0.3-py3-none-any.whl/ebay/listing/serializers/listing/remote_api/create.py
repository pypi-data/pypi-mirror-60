from ebay.listing.serializers.listing.remote_api.listing import EbayListingSerializer


class CreateEbayListingSerializer(EbayListingSerializer):
    class Meta(EbayListingSerializer.Meta):
        pass
