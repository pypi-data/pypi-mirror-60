from rest_framework import serializers

from etsy.policy.serializers.shipping.base import (
    BaseEtsyShippingTemplateSerializer,
    BaseEtsyShippingTemplateEntrySerializer,
)


class CreateOrUpdateEtsyShippingTemplateEntrySerializer(
    BaseEtsyShippingTemplateEntrySerializer
):
    class Meta:
        model = BaseEtsyShippingTemplateEntrySerializer.Meta.model
        fields = [
            "destination_country",
            "primary_cost",
            "secondary_cost",
            "destination_region",
        ]

    def validate(self, attrs: dict):
        if "destination_country" in attrs and "destination_region" in attrs:
            raise serializers.ValidationError(
                {
                    "destination": (
                        "В политике доставки может быть указана либо страна, либо регион."
                    )
                }
            )
        return attrs

    def create(self, validated_data):
        shipping_template_id = validated_data.pop("shipping_template_id", None)
        destination_country = validated_data.pop("destination_country", None)
        destination_region = validated_data.pop("destination_region", None)

        kwargs = {
            "shipping_template_id": shipping_template_id,
            "defaults": validated_data,
        }

        if destination_country:
            kwargs["destination_country"] = destination_country

        if destination_region:
            kwargs["destination_region"] = destination_region

        instance, created = self.Meta.model.objects.update_or_create(**kwargs)
        return instance

    def to_representation(self, instance):
        return BaseEtsyShippingTemplateEntrySerializer().to_representation(instance)


class CreateEtsyShippingTemplateSerializer(BaseEtsyShippingTemplateSerializer):
    class Meta:
        model = BaseEtsyShippingTemplateSerializer.Meta.model
        fields = [
            "marketplace_user_account",
            "title",
            "origin_country",
            "min_processing_days",
            "max_processing_days",
        ]

    def create(self, validated_data):
        instance = self.Meta.model.objects.create(**validated_data)
        return instance

    def to_representation(self, instance):
        return BaseEtsyShippingTemplateSerializer().to_representation(instance)
