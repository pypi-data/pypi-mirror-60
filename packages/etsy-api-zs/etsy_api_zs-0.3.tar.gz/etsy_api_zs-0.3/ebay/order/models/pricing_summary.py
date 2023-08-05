from django.db import models

from ebay.models.abstract import AbstractAmount
from ebay.order.models import EbayOrder


class PricingSummary(models.Model):
    order = models.OneToOneField(
        EbayOrder, on_delete=models.CASCADE, related_name="pricing_summary"
    )


class Adjustment(AbstractAmount):
    pricing_summary = models.OneToOneField(
        PricingSummary, on_delete=models.CASCADE, related_name="adjustment"
    )


class DeliveryCost(AbstractAmount):
    pricing_summary = models.OneToOneField(
        PricingSummary, on_delete=models.CASCADE, related_name="delivery_cost"
    )


class DeliveryDiscount(AbstractAmount):
    pricing_summary = models.OneToOneField(
        PricingSummary, on_delete=models.CASCADE, related_name="delivery_discount"
    )


class Fee(AbstractAmount):
    pricing_summary = models.OneToOneField(
        PricingSummary, on_delete=models.CASCADE, related_name="fee"
    )


class PriceDiscountSubtotal(AbstractAmount):
    pricing_summary = models.OneToOneField(
        PricingSummary, on_delete=models.CASCADE, related_name="price_discount_subtotal"
    )


class PriceSubtotal(AbstractAmount):
    pricing_summary = models.OneToOneField(
        PricingSummary, on_delete=models.CASCADE, related_name="price_subtotal"
    )


class Tax(AbstractAmount):
    pricing_summary = models.OneToOneField(
        PricingSummary, on_delete=models.CASCADE, related_name="tax"
    )


class Total(AbstractAmount):
    pricing_summary = models.OneToOneField(
        PricingSummary, on_delete=models.CASCADE, related_name="total"
    )
