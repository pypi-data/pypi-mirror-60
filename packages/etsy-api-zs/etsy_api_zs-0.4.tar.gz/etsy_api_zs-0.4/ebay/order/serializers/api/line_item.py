from ebay.data import enums
from ebay.order.models import (
    AppliedPromotion,
    EbayOrderLineItem,
    LineItemDeliveryCost,
    LineItemFulfillmentInstructions,
    LineItemProperties,
    LineItemRefund,
    LineItemTax,
)
from rest_framework import serializers

from .base import AmountSerializer


class LineItemDeliveryCostSerializer(serializers.ModelSerializer):
    importCharges = AmountSerializer(required=False, source="import_charges")
    shippingCost = AmountSerializer(source="shipping_cost")
    shippingIntermediationFee = AmountSerializer(
        required=False, source="shipping_intermediation_fee"
    )

    class Meta:
        model = LineItemDeliveryCost
        fields = ["importCharges", "shippingCost", "shippingIntermediationFee"]


class LineItemFulfillmentInstructionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItemFulfillmentInstructions
        fields = [
            "destinationTimeZone",
            "guaranteedDelivery",
            "maxEstimatedDeliveryDate",
            "minEstimatedDeliveryDate",
            "shipByDate",
            "sourceTimeZone",
        ]


class LineItemPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItemProperties
        fields = ["buyerProtection", "fromBestOffer", "soldViaAdCampaign"]


class LineItemRefundSerializer(serializers.ModelSerializer):
    amount = AmountSerializer(required=False)

    class Meta:
        model = LineItemRefund
        fields = [
            "amount",
            "refundDate",
            "refundId" "refundReferenceId",
        ]


class LineItemTaxSerializer(serializers.ModelSerializer):
    amount = AmountSerializer(required=False)

    class Meta:
        model = LineItemTax
        fields = ["amount"]


class AppliedPromotionSerializer(serializers.Serializer):
    description = serializers.CharField(required=False)
    discountAmount = AmountSerializer(required=False, source="discount_amount")
    promotionId = serializers.CharField(required=False)

    class Meta:
        model = AppliedPromotion
        fields = ["description", "discountAmount", "promotionId"]


class LineItemSerializer(serializers.ModelSerializer):
    appliedPromotions = AppliedPromotionSerializer(
        many=True, source="applied_promotions"
    )
    deliveryCost = LineItemDeliveryCostSerializer(source="delivery_cost")
    discountedLineItemCost = AmountSerializer(
        required=False, source="discounted_line_item_cost"
    )
    lineItemCost = AmountSerializer(source="line_item_cost")
    lineItemFulfillmentInstructions = LineItemFulfillmentInstructionsSerializer(
        required=False, source="line_item_fulfillment_instructions"
    )
    lineItemFulfillmentStatus = serializers.ChoiceField(
        choices=enums.LineItemFulfillmentStatusEnum
    )
    properties = LineItemPropertiesSerializer()
    refunds = LineItemRefundSerializer(many=True, required=False)
    soldFormat = serializers.ChoiceField(choices=enums.SoldFormatEnum)
    taxes = LineItemTaxSerializer(many=True)
    total = AmountSerializer()

    class Meta:
        model = EbayOrderLineItem
        fields = [
            "appliedPromotions",
            "deliveryCost",
            "discountedLineItemCost",
            "legacyItemId",
            "legacyVariationId",
            "lineItemCost",
            "lineItemFulfillmentInstructions",
            "lineItemFulfillmentStatus",
            "lineItemId",
            "listingMarketplaceId",
            "properties",
            "purchaseMarketplaceId",
            "quantity",
            "refunds",
            "sku",
            "soldFormat",
            "taxes",
            "title",
            "total",
        ]
