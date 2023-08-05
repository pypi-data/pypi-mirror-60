from ebay.order.models import PricingSummary
from ebay.order.serializers.api.base import AmountSerializer
from rest_framework import serializers


class PricingSummarySerializer(serializers.ModelSerializer):
    adjustment = AmountSerializer(required=False)
    deliveryCost = AmountSerializer(required=False, source="delivery_cost")
    deliveryDiscount = AmountSerializer(required=False, source="delivery_discount")
    fee = AmountSerializer(required=False)
    priceDiscountSubtotal = AmountSerializer(
        required=False, source="price_discount_subtotal"
    )
    priceSubtotal = AmountSerializer(source="price_subtotal")
    tax = AmountSerializer(required=False)
    total = AmountSerializer()

    class Meta:
        model = PricingSummary
        fields = [
            "adjustment",
            "deliveryCost",
            "deliveryDiscount",
            "fee",
            "priceDiscountSubtotal",
            "priceSubtotal",
            "tax",
            "total",
        ]
