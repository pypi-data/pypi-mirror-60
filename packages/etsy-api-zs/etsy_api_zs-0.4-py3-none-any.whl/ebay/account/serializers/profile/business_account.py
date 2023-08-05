from ebay.account import models
from rest_framework import serializers


class BusinessSecondaryPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BusinessSecondaryPhone
        exclude = [
            "id",
            "business_account",
        ]


class BusinessPrimaryPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BusinessPrimaryPhone
        exclude = [
            "id",
            "business_account",
        ]


class BusinessPrimaryContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BusinessPrimaryContact
        exclude = [
            "id",
            "business_account",
        ]


class BusinessAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BusinessAddress
        exclude = [
            "id",
            "business_account",
        ]


class BusinessAccountSerializer(serializers.ModelSerializer):
    address = BusinessAddressSerializer(required=False)
    primaryContact = BusinessPrimaryContactSerializer(required=False)
    primaryPhone = BusinessPrimaryPhoneSerializer(required=False)
    secondaryPhone = BusinessSecondaryPhoneSerializer(required=False)

    class Meta:
        model = models.BusinessAccount
        exclude = ["id", "profile"]
