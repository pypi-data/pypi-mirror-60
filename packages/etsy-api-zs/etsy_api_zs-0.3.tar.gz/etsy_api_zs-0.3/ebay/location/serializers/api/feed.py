from collections import OrderedDict

from ebay.location.models import EbayLocation
from rest_framework import serializers


class EbayLocationFlatSerializer(serializers.ModelSerializer):
    """
    Serializer for flat-file representation
    """

    merchantLocationKey = serializers.CharField(label="Location ID")
    name = serializers.CharField(label="Name", required=False)
    addressLine1 = serializers.CharField(label="Address 1")
    addressLine2 = serializers.CharField(label="Address 2", required=False)
    city = serializers.CharField(label="City")
    countryCode = serializers.CharField(label="Country")
    postalCode = serializers.CharField(label="Postal Code", required=False)
    latitude = serializers.CharField(label="Latitude", required=False)
    longitude = serializers.CharField(label="Longitude", required=False)
    utcOffset = serializers.CharField(label="UTC Offset", required=False)
    phone = serializers.CharField(label="Phone", required=False)
    locationWebUrl = serializers.CharField(label="url", required=False)
    merchantLocationStatus = serializers.CharField(label="Status", required=False)

    class Meta:
        model = EbayLocation
        fields = [
            "merchantLocationKey",
            "name",
            "addressLine1",
            "addressLine2",
            "city",
            "countryCode",
            "postalCode",
            "latitude",
            "longitude",
            "utcOffset",
            "phone",
            "locationWebUrl",
            "merchantLocationStatus",
        ]

    def __new__(cls, *args, **kwargs):
        if kwargs.pop("many", False):
            raise AttributeError("Аргумент many=True не поддерживается.")
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, "initial_data"):
            self.initial_data = self.transform_initial_data()

    def transform_initial_data(self):
        initial_data = {}
        for field_name, field_properties in self.fields.items():
            val = self.initial_data.get(field_properties.label, None)
            if val:
                initial_data[field_name] = val
        return initial_data

    def to_representation(self, instance):
        return_data = super().to_representation(instance)
        copy = OrderedDict()
        for key, value in return_data.items():
            copy[self.fields.get(key).label] = value
        return copy

    def create(self, validated_data):
        location, created = self.Meta.model.objects.update_or_create(**validated_data)
        return location
