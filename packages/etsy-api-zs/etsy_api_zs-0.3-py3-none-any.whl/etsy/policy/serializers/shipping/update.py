from etsy.policy.serializers.shipping.base import BaseEtsyShippingTemplateSerializer


class UpdateEtsyShippingTemplateSerializer(BaseEtsyShippingTemplateSerializer):
    class Meta:
        model = BaseEtsyShippingTemplateSerializer.Meta.model
        fields = [
            "title",
            "origin_country",
            "min_processing_days",
            "max_processing_days",
        ]

    def update(self, instance, validated_data):
        instance, updated = self.Meta.model.objects.update_or_create(
            id=instance.id, defaults=validated_data
        )
        return instance
