from ebay.account import models
from rest_framework import serializers


class IndividualSecondaryPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IndividualSecondaryPhone
        exclude = [
            "id",
            "individual_account",
        ]


class IndividualRegistrationAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IndividualRegistrationAddress
        exclude = [
            "id",
            "individual_account",
        ]


class IndividualPrimaryPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IndividualPrimaryPhone
        exclude = [
            "id",
            "individual_account",
        ]


class IndividualAccountSerializer(serializers.ModelSerializer):
    primaryPhone = IndividualPrimaryPhoneSerializer(required=False)
    registrationAddress = IndividualRegistrationAddressSerializer(required=False)
    secondaryPhone = IndividualSecondaryPhoneSerializer(required=False)

    class Meta:
        model = models.IndividualAccount
        exclude = ["id", "profile"]
