from ebay.order.models import EbayShippingFulfillment, EbayShippingFulfillmentLineItem
from rest_framework import serializers


class EbayShippingFulfillmentLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EbayShippingFulfillmentLineItem
        fields = "__all__"


class EbayShippingFulfillmentSerializer(serializers.ModelSerializer):
    line_items = EbayShippingFulfillmentLineItemSerializer(required=False, many=True)

    class Meta:
        model = EbayShippingFulfillment
        exclude = ["order"]
