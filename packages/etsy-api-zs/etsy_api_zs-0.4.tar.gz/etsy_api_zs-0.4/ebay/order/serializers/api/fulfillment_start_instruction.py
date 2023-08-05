from ebay.order.models import FulfillmentStartInstruction, ShippingStep, ShipTo
from ebay.order.serializers.api.base import AddressSerializer
from rest_framework import serializers


class PrimaryPhoneSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField(required=False)


class ShipToSerializer(serializers.ModelSerializer):
    contactAddress = AddressSerializer(source="contact_address")
    primaryPhone = PrimaryPhoneSerializer(required=False)

    class Meta:
        model = ShipTo
        fields = [
            "companyName",
            "contactAddress",
            "email",
            "fullName",
            "primaryPhone",
        ]


class ShippingStepSerializer(serializers.ModelSerializer):
    shipTo = ShipToSerializer(source="ship_to")

    class Meta:
        model = ShippingStep
        fields = [
            "shippingCarrierCode",
            "shippingServiceCode",
            "shipToReferenceId",
            "shipTo",
        ]


class PickupStepSerializer(serializers.Serializer):
    merchantLocationKey = serializers.CharField(required=False)


class FulfillmentStartInstructionSerializer(serializers.ModelSerializer):
    finalDestinationAddress = AddressSerializer(
        required=False, source="final_destination_address"
    )
    shippingStep = ShippingStepSerializer(required=False, source="shipping_step")
    pickupStep = PickupStepSerializer(required=False, source="*")

    class Meta:
        model = FulfillmentStartInstruction
        fields = [
            "destinationTimeZone",
            "ebaySupportedFulfillment",
            "finalDestinationAddress",
            "fulfillmentInstructionsType",
            "maxEstimatedDeliveryDate",
            "minEstimatedDeliveryDate",
            "shippingStep",
            "pickupStep",
        ]
