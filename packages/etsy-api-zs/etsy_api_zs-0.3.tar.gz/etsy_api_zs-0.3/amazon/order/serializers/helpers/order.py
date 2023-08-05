from typing import Tuple

from amazon.order.models import AmazonOrder, AmazonShippingAddress


def update_or_create_amazon_order(defaults: dict, **kwargs) -> Tuple[AmazonOrder, bool]:
    shipping_address_data = defaults.pop("shipping_address", None)
    instance: AmazonOrder
    created: bool
    # Update or create AmazonOrder
    instance, created = AmazonOrder.objects.update_or_create(
        **kwargs, defaults=defaults
    )
    # Update or create AmazonShippingAddress
    if shipping_address_data:
        instance, created = update_or_create_amazon_shipping_address(
            order=instance, defaults=shipping_address_data
        )
    return instance, created


def update_or_create_amazon_shipping_address(
    order: AmazonOrder, defaults: dict,
) -> Tuple[AmazonShippingAddress, bool]:
    instance: AmazonShippingAddress
    created: bool
    instance, created = AmazonShippingAddress.objects.update_or_create(
        order=order, defaults=defaults
    )
    return instance, created
