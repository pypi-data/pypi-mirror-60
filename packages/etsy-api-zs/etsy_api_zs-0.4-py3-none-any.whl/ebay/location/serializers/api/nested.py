from ebay.data.enums import LocationTypeEnum
from ebay.location.models import EbayLocation
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from zonesmart.data.enums import CountryCodeEnum
from zonesmart.serializers import NotNullAndEmptyStringModelSerializer


class AddressSerializer(serializers.Serializer):
    addressLine1 = serializers.CharField(max_length=128, required=False)
    addressLine2 = serializers.CharField(max_length=128, required=False)
    city = serializers.CharField(max_length=128, required=False)
    countryCode = serializers.ChoiceField(choices=CountryCodeEnum, required=False)
    county = serializers.CharField(required=False)
    postalCode = serializers.CharField(max_length=16, required=False)
    stateOrProvince = serializers.CharField(max_length=128, required=False)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["country"] = representation.pop("countryCode", None)
        return ReturnDict(representation, serializer=self)


class LocationSerializer(serializers.Serializer):
    address = AddressSerializer(source="*", required=False)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return ReturnDict(representation, serializer=self)


class EbayLocationNestedSerializer(NotNullAndEmptyStringModelSerializer):
    location = LocationSerializer(source="*", required=False)
    locationTypes = serializers.MultipleChoiceField(
        choices=LocationTypeEnum, required=False
    )

    class Meta:
        model = EbayLocation
        fields = [
            "name",
            "merchantLocationKey",
            "locationTypes",
            "location",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["locationTypes"] = list(representation.pop("locationTypes"))
        return representation
