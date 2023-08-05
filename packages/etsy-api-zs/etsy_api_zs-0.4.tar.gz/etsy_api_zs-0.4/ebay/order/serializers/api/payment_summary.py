from ebay.order.models import (
    OrderRefund,
    Payment,
    PaymentHold,
    PaymentSummary,
    SellerActionsToRelease,
)
from ebay.order.serializers.api.base import AmountSerializer
from rest_framework import serializers


class OrderRefundSerializer(serializers.ModelSerializer):
    amount = AmountSerializer(required=False)

    class Meta:
        model = OrderRefund
        fields = [
            "amount",
            "refundDate",
            "refundReferenceId",
            "refundStatus",
            "refundId",
        ]


class SellerActionsToReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerActionsToRelease
        fields = ["sellerActionToRelease"]


class PaymentHoldSerializer(serializers.ModelSerializer):
    holdAmount = AmountSerializer(required=False, source="amount")
    sellerActionsToRelease = SellerActionsToReleaseSerializer(
        required=False, many=True, source="seller_actions_to_release"
    )

    class Meta:
        model = PaymentHold
        fields = [
            "expectedReleaseDate",
            "holdAmount",
            "holdReason",
            "holdState",
            "releaseDate",
            "sellerActionsToRelease",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    amount = AmountSerializer()
    paymentHolds = PaymentHoldSerializer(
        required=False, many=True, source="payment_holds"
    )

    class Meta:
        model = Payment
        fields = [
            "amount",
            "paymentDate",
            "paymentHolds",
            "paymentMethod",
            "paymentReferenceId",
            "paymentStatus",
        ]


class PaymentSummarySerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True)
    refunds = OrderRefundSerializer(many=True)
    totalDueSeller = AmountSerializer(source="total_due_seller")

    class Meta:
        model = PaymentSummary
        fields = ["payments", "refunds", "totalDueSeller"]
