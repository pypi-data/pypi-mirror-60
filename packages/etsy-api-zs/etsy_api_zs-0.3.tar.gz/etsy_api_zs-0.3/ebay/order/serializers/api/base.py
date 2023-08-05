# from ebay.data import enums
from ebay.models.abstract import AbstractAddress, AbstractAmount
from rest_framework import serializers


class AmountSerializer(serializers.Serializer):
    # convertedFromCurrency = serializers.ChoiceField(required=False, choices=enums.CurrencyCodeEnum)
    # convertedFromValue = serializers.FloatField(required=False)
    # currency = serializers.ChoiceField(choices=enums.CurrencyCodeEnum)
    # value = serializers.FloatField()

    class Meta:
        model = AbstractAmount
        fields = ["convertedFromCurrency", "convertedFromValue", "currency", "value"]


class AddressSerializer(serializers.Serializer):
    # addressLine1 = serializers.CharField(required=False)
    # addressLine2 = serializers.CharField(required=False)
    # city = serializers.CharField(required=False)
    # countryCode = serializers.ChoiceField(choices=enums.CountryCodeEnum)
    # county = serializers.CharField(required=False)
    # postalCode = serializers.CharField(required=False)
    # stateOrProvince = serializers.CharField(required=False)

    class Meta:
        model = AbstractAddress
        fields = [
            "addressLine1",
            "addressLine2",
            "city",
            "countryCode",
            "county",
            "postalCode",
            "stateOrProvince",
        ]
