from ebay.order.models import (
    EbayOrderLineItem,
    EbayShippingFulfillment,
    EbayShippingFulfillmentLineItem,
)
from rest_framework import serializers


class EbayShippingFulfillmentLineItemSerializer(serializers.ModelSerializer):
    lineItemId = serializers.CharField()

    class Meta:
        model = EbayShippingFulfillmentLineItem
        fields = [
            "lineItemId",
        ]


class EbayShippingFulfillmentDownloadSerializer(serializers.ModelSerializer):
    lineItems = EbayShippingFulfillmentLineItemSerializer(many=True)
    shippingCarrierCode = serializers.CharField(required=False)
    shippingServiceCode = serializers.CharField(required=False)

    class Meta:
        model = EbayShippingFulfillment
        fields = [
            "fulfillmentId",
            "shippedDate",
            "shippingCarrierCode",
            "shippingServiceCode",
            "shipmentTrackingNumber",
            "lineItems",
        ]

    def create(self, validated_data):
        order = validated_data["order"]
        line_item_data_list = validated_data.pop("lineItems")
        shipping_fulfillment, created = self.Meta.model.objects.update_or_create(
            order=order,
            fulfillmentId=validated_data["fulfillmentId"],
            defaults=validated_data,
        )
        for line_item_data in line_item_data_list:
            if EbayOrderLineItem.objects.filter(
                lineItemId=line_item_data["lineItemId"]
            ).exists():
                EbayShippingFulfillmentLineItem.objects.update_or_create(
                    shipping_fulfillment=shipping_fulfillment,
                    line_item=EbayOrderLineItem.objects.get(
                        lineItemId=line_item_data["lineItemId"]
                    ),
                )
        return shipping_fulfillment
