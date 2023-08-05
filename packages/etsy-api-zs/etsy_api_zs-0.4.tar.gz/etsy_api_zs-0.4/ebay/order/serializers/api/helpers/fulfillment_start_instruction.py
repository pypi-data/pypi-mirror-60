from typing import Tuple

from ebay.order.models import (
    ContactAddress,
    EbayOrder,
    FinalDestinationAddress,
    FulfillmentStartInstruction,
    ShippingStep,
    ShipTo,
)


def update_or_create_fulfillment_start_instruction(
    order: EbayOrder, data: dict
) -> Tuple[FulfillmentStartInstruction, bool]:
    final_destination_address_data = data.pop("finalDestinationAddress", None)
    shipping_step_data = data.pop("shipping_step", None)
    # FulfillmentStartInstruction
    instance: FulfillmentStartInstruction
    created: bool
    instance, created = FulfillmentStartInstruction.objects.update_or_create(
        order=order, defaults=data
    )
    # FinalDestinationAddress
    if final_destination_address_data:
        update_or_create_final_destination_address(
            fulfillment_start_instruction=instance, data=final_destination_address_data
        )
    # ShippingStep
    update_or_create_shipping_step(
        fulfillment_start_instruction=instance, data=shipping_step_data
    )
    return instance, created


def update_or_create_final_destination_address(
    fulfillment_start_instruction: FulfillmentStartInstruction, data: dict
) -> Tuple[FinalDestinationAddress, bool]:
    instance: FinalDestinationAddress
    created: bool
    return FinalDestinationAddress.objects.update_or_create(
        fulfillment_start_instruction=fulfillment_start_instruction, defaults=data
    )


def update_or_create_shipping_step(
    fulfillment_start_instruction: FulfillmentStartInstruction, data: dict
) -> Tuple[ShippingStep, bool]:
    ship_to_data = data.pop("ship_to")
    primary_phone_data = ship_to_data.pop("primaryPhone")
    ship_to_data["phoneNumber"] = primary_phone_data["phoneNumber"]
    # ShippingStep update or create
    instance: ShippingStep
    created: bool
    instance, created = ShippingStep.objects.update_or_create(
        fulfillment_start_instruction=fulfillment_start_instruction, defaults=data
    )
    # ShipTo update or create
    update_or_create_ship_to(shipping_step=instance, data=ship_to_data)
    return instance, created


def update_or_create_ship_to(
    shipping_step: ShippingStep, data: dict
) -> Tuple[ShipTo, bool]:
    contact_address_data = data.pop("contact_address", None)
    # ShipTo update or create
    instance: ShipTo
    created: bool
    instance, created = ShipTo.objects.update_or_create(
        shipping_step=shipping_step, defaults=data
    )
    # ContactAddress update or create
    if contact_address_data:
        update_or_create_contact_address(ship_to=instance, data=contact_address_data)
    return instance, created


def update_or_create_contact_address(
    ship_to: ShipTo, data: dict
) -> Tuple[ContactAddress, bool]:
    instance: ContactAddress
    created: bool
    instance, created = ContactAddress.objects.update_or_create(
        ship_to=ship_to, defaults=data
    )
    return instance, created
