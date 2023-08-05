from rest_framework import serializers

from etsy.policy.models import EtsyShippingTemplate, EtsyShippingTemplateEntry


class BaseEtsyShippingTemplateEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = EtsyShippingTemplateEntry
        exclude = ["shipping_template", "is_removed"]


class BaseEtsyShippingTemplateSerializer(serializers.ModelSerializer):
    entries = BaseEtsyShippingTemplateEntrySerializer(many=True)

    class Meta:
        model = EtsyShippingTemplate
        fields = "__all__"
