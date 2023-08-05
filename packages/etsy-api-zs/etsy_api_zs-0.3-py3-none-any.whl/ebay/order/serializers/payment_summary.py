from ebay.order.models import (
    HoldAmount,
    OrderRefund,
    OrderRefundAmount,
    Payment,
    PaymentAmount,
    PaymentHold,
    PaymentSummary,
    SellerActionsToRelease,
    TotalDueSeller,
)
from rest_framework import serializers


class TotalDueSellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TotalDueSeller
        exclude = ["id", "payment_summary"]


class OrderRefundAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderRefundAmount
        exclude = ["id", "order_refund"]


class OrderRefundSerializer(serializers.ModelSerializer):
    amount = OrderRefundAmountSerializer(required=False)

    class Meta:
        model = OrderRefund
        exclude = ["id", "payment_summary"]


class SellerActionsToReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerActionsToRelease
        exclude = ["id", "payment_hold"]


class HoldAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = HoldAmount
        exclude = ["id", "payment_hold"]


class PaymentHoldSerializer(serializers.ModelSerializer):
    amount = HoldAmountSerializer(required=False)
    seller_actions_to_release = SellerActionsToReleaseSerializer(
        required=False, many=True
    )

    class Meta:
        model = PaymentHold
        exclude = ["id", "payment"]


class PaymentAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAmount
        exclude = ["id", "payment"]


class PaymentSerializer(serializers.ModelSerializer):
    amount = PaymentAmountSerializer(required=False)
    payment_holds = PaymentHoldSerializer(required=False, many=True)

    class Meta:
        model = Payment
        exclude = ["id", "payment_summary"]


class PaymentSummarySerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(required=False, many=True)
    refunds = OrderRefundSerializer(required=False, many=True)
    total_due_seller = TotalDueSellerSerializer(required=False)

    class Meta:
        model = PaymentSummary
        exclude = ["id", "order"]
