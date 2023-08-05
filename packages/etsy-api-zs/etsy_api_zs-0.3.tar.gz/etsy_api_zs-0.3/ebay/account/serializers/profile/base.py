from ebay.account import models
from ebay.account.serializers.profile.business_account import BusinessAccountSerializer
from ebay.account.serializers.profile.individual_account import (
    IndividualAccountSerializer,
)
from rest_framework import serializers


class EbayUserAccountProfileSerializer(serializers.ModelSerializer):
    businessAccount = BusinessAccountSerializer(required=False)
    individualAccount = IndividualAccountSerializer(required=False)

    class Meta:
        model = models.EbayUserAccountProfile
        exclude = [
            "id",
        ]
        extra_kwargs = {
            "ebay_user_account": {
                "required": False,
                "write_only": True,
                "validators": [],
            }
        }

    def create(self, validated_data):
        instance, created = self.Meta.model.objects.update_or_create(
            ebay_user_account=validated_data.pop("ebay_user_account"),
            defaults=validated_data,
        )
        return instance
