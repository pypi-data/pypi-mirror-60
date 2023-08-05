from etsy.policy.models import EtsyShippingTemplate
from etsy.policy.serializers.shipping.base import (
    BaseEtsyShippingTemplateSerializer,
    BaseEtsyShippingTemplateEntrySerializer,
)


class RemoteCreateEtsyShippingTemplateEntrySerializer(
    BaseEtsyShippingTemplateEntrySerializer
):
    class Meta:
        model = BaseEtsyShippingTemplateEntrySerializer.Meta.model
        fields = [
            "destination_country_id",
            "destination_region_id",
            "primary_cost",
            "secondary_cost",
        ]


class RemoteCreateEtsyShippingTemplateSerializer(BaseEtsyShippingTemplateSerializer):
    entries = RemoteCreateEtsyShippingTemplateEntrySerializer(many=True)

    class Meta:
        model = EtsyShippingTemplate
        fields = [
            "title",
            "origin_country_id",
            "min_processing_days",
            "max_processing_days",
            "entries",
        ]
