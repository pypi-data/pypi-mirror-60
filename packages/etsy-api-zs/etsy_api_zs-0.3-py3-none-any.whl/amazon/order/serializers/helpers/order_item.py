from typing import Tuple

from amazon.order.models import AmazonOrder, AmazonOrderItem, Money
from amazon.order.models.order_item import (
    GiftWrapPrice,
    GiftWrapTax,
    ItemPrice,
    ItemTax,
    PromotionDiscount,
    ShippingDiscount,
    ShippingPrice,
    ShippingTax,
)

MONEY_DATA_KEY_MODEL_PAIRS = {
    "item_price": ItemPrice,
    "shipping_price": ShippingPrice,
    "gift_wrap_price": GiftWrapPrice,
    "item_tax": ItemTax,
    "shipping_tax": ShippingTax,
    "gift_wrap_tax": GiftWrapTax,
    "shipping_discount": ShippingDiscount,
    "promotion_discount": PromotionDiscount,
}


def update_or_create_order_item(
    order: AmazonOrder, data: dict
) -> Tuple[AmazonOrderItem, bool]:
    order_item_id = data.pop("OrderItemId")
    # Pop Money data
    money_to_create = dict()
    for money_data_key, money_model in MONEY_DATA_KEY_MODEL_PAIRS.items():
        money_data = data.pop(money_data_key, None)
        if money_data:
            money_to_create[money_data_key] = {"model": money_model, "data": money_data}
    # AmazonOrderItem update or create
    instance: AmazonOrderItem
    created: bool
    instance, created = AmazonOrderItem.objects.update_or_create(
        order=order, OrderItemId=order_item_id, defaults=data
    )
    # Money update or create
    if money_to_create:
        for money_data in money_to_create.values():
            update_or_create_money(
                model=money_data["model"], order_item=instance, data=money_data["data"]
            )
    return instance, created


def update_or_create_money(
    model: Money, order_item: AmazonOrderItem, data: dict
) -> Tuple[Money, bool]:
    instance: Money
    created: bool
    instance, created = model.objects.update_or_create(
        order_item=order_item, defaults=data
    )
    return instance, created
