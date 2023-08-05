from datetime import datetime

from django.utils.timezone import make_aware

from etsy.listing.serializers.etsy_listing.remote_api.base import (
    BaseEtsyListingSerializer,
)


class DownloadEtsyListingSerializer(BaseEtsyListingSerializer):
    class Meta(BaseEtsyListingSerializer.Meta):
        exclude = BaseEtsyListingSerializer.Meta.exclude + [
            "channel",
            "base_product",
            "shop_section",
            "category",
        ]

    def to_internal_value(self, data):
        for field in [
            "creation_tsz",
            "ending_tsz",
            "original_creation_tsz",
            "last_modified_tsz",
            "state_tsz",
        ]:
            if field in data:
                data[field] = make_aware(datetime.fromtimestamp(data[field]))
        return super().to_internal_value(data)
