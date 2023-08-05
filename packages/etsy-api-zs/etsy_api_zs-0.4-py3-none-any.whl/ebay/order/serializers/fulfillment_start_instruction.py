from ebay.order.models import (
    ContactAddress,
    FinalDestinationAddress,
    FulfillmentStartInstruction,
    ShippingStep,
    ShipTo,
)
from rest_framework import serializers


class ContactAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactAddress
        exclude = ["id", "ship_to"]


class ShipToSerializer(serializers.ModelSerializer):
    contact_address = ContactAddressSerializer(required=False)

    class Meta:
        model = ShipTo
        exclude = ["id", "shipping_step"]


class ShippingStepSerializer(serializers.ModelSerializer):
    ship_to = ShipToSerializer(required=False)

    class Meta:
        model = ShippingStep
        exclude = [
            "id",
            "fulfillment_start_instruction",
        ]


class FinalDestinationAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalDestinationAddress
        exclude = ["id", "fulfillment_start_instruction"]


class FulfillmentStartInstructionSerializer(serializers.ModelSerializer):
    final_destination_address = FinalDestinationAddressSerializer(required=False)
    shipping_step = ShippingStepSerializer(required=False)

    class Meta:
        model = FulfillmentStartInstruction
        exclude = ["id", "order"]
