from ebay.data import enums
from ebay.location.models import EbayLocation
from rest_framework import serializers


class BaseEbayLocationSerializer(serializers.ModelSerializer):
    # countryCode = serializers.CharField(source='country')
    locationTypes = serializers.MultipleChoiceField(
        choices=enums.LocationTypeEnum, required=False
    )

    class Meta:
        model = EbayLocation
        fields = [
            "id",
            "marketplace_user_account",
            "name",
            "phone",
            "merchantLocationKey",
            "locationTypes",
            "status",
            "addressLine1",
            "addressLine2",
            "city",
            "countryCode",
            "county",
            "postalCode",
            "stateOrProvince",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        marketplace_user_account = validated_data.pop("marketplace_user_account")
        merchant_location_key = validated_data.pop("merchantLocationKey", None)

        if merchant_location_key:
            location, created = self.Meta.model.objects.update_or_create(
                marketplace_user_account=marketplace_user_account,
                merchantLocationKey=merchant_location_key,
                defaults=validated_data,
            )
        else:
            location = self.Meta.model.objects.create(
                marketplace_user_account=marketplace_user_account, **validated_data
            )

        return location

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["locationTypes"] = list(representation.pop("locationTypes"))
        return representation
