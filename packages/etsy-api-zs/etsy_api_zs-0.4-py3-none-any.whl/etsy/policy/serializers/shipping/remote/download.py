from etsy.policy.serializers.shipping.base import (
    BaseEtsyShippingTemplateSerializer,
    BaseEtsyShippingTemplateEntrySerializer,
)


class RemoteDownloadEtsyShippingTemplateEntrySerializer(
    BaseEtsyShippingTemplateEntrySerializer
):
    class Meta(BaseEtsyShippingTemplateEntrySerializer.Meta):
        pass


class RemoteDownloadEtsyShippingTemplateSerializer(BaseEtsyShippingTemplateSerializer):
    entries = RemoteDownloadEtsyShippingTemplateEntrySerializer(many=True)

    class Meta:
        model = BaseEtsyShippingTemplateSerializer.Meta.model
        exclude = [
            "id",
            "marketplace_user_account",
        ]
        extra_kwargs = {"shipping_template_id": {"validators": []}}

    def create(self, validated_data):
        shipping_template_id = validated_data.pop("shipping_template_id")
        validated_data["status"] = "published"
        instance, created = self.Meta.model.nested_objects.update_or_create(
            shipping_template_id=shipping_template_id, defaults=validated_data
        )
        return instance
