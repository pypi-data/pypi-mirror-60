from ebay.order.models import EbayOrder
from ebay.order.serializers import (
    CancelStatusSerializer,
    EbayOrderLineItemSerializer,
    FulfillmentStartInstructionSerializer,
    PaymentSummarySerializer,
    PricingSummarySerializer,
)
from rest_framework import serializers


class BaseEbayOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = EbayOrder
        fields = [
            "id",
            "marketplace_user_account",
            "orderId",
            "buyer_username",
            "buyerCheckoutNotes",
            "creationDate",
            "ebayCollectAndRemitTax",
            "fulfillment_hrefs",
            "lastModifiedDate",
            "legacyOrderId",
            "orderFulfillmentStatus",
            "orderId",
            "orderPaymentStatus",
            "salesRecordReference",
            "sellerId",
        ]


class RetrieveEbayOrderSerializer(BaseEbayOrderSerializer):
    cancel_status = CancelStatusSerializer(required=False)
    fulfillment_start_instructions = FulfillmentStartInstructionSerializer(
        required=False, many=True
    )
    line_items = EbayOrderLineItemSerializer(required=False, many=True)
    payment_summary = PaymentSummarySerializer(required=False)
    pricing_summary = PricingSummarySerializer(required=False)

    class Meta(BaseEbayOrderSerializer.Meta):
        fields = BaseEbayOrderSerializer.Meta.fields + [
            "cancel_status",
            "fulfillment_start_instructions",
            "line_items",
            "payment_summary",
            "pricing_summary",
        ]
