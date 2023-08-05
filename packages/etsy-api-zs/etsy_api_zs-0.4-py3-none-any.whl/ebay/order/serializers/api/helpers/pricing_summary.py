from typing import Tuple, Type

from ebay.models.abstract import AbstractAmount
from ebay.order.models import (
    Adjustment,
    DeliveryCost,
    DeliveryDiscount,
    EbayOrder,
    Fee,
    PriceDiscountSubtotal,
    PriceSubtotal,
    PricingSummary,
    Tax,
    Total,
)

AMOUNT_KEYS = (
    (Adjustment, "adjustment"),
    (DeliveryCost, "delivery_cost"),
    (DeliveryDiscount, "delivery_discount"),
    (Fee, "fee"),
    (PriceDiscountSubtotal, "price_discount_subtotal"),
    (PriceSubtotal, "price_subtotal"),
    (Tax, "tax"),
    (Total, "total"),
)


def update_or_create_pricing_summary(
    order: EbayOrder, data: dict
) -> Tuple[PricingSummary, bool]:
    amount_create_dict = dict()
    for key in AMOUNT_KEYS:
        amount_key_name = key[1]
        amount_data = data.pop(amount_key_name, None)
        if amount_data:
            amount_create_dict[key[0]] = amount_data
    instance: PricingSummary
    created: bool
    instance, created = PricingSummary.objects.update_or_create(
        order=order, defaults=data
    )
    # Update or create amounts models
    if amount_create_dict:
        for model, data in amount_create_dict.items():
            update_or_create_amount(model=model, pricing_summary=instance, data=data)
    return instance, created


def update_or_create_amount(
    model: Type[AbstractAmount], pricing_summary: PricingSummary, data: dict
) -> Tuple[AbstractAmount, bool]:
    instance: model
    created: bool
    instance, created = model.objects.update_or_create(
        pricing_summary=pricing_summary, defaults=data
    )
    return instance, created
