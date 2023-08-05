from ebay.policy import models
from ebay.policy.serializers import (
    AbstractCategoryTypeSerializer,
    AbstractPolicySerializer,
)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class BaseFulfillmentPolicyRegionIncludedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FulfillmentPolicyRegionIncluded
        exclude = ["id", "ship_to_locations"]


class BaseFulfillmentPolicyRegionExcludedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FulfillmentPolicyRegionExcluded
        exclude = ["id", "ship_to_locations"]


class BaseFulfillmentPolicyShipToLocationsSerializer(serializers.ModelSerializer):
    regionExcluded = BaseFulfillmentPolicyRegionExcludedSerializer(
        required=False, many=True
    )
    regionIncluded = BaseFulfillmentPolicyRegionIncludedSerializer(
        required=False, many=True
    )

    class Meta:
        model = models.FulfillmentPolicyShipToLocations
        exclude = ["id", "fulfillment_policy"]


class BaseSurchargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Surcharge
        exclude = ["id", "shipping_service"]


class BaseShippingServiceRegionIncludedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ShippingServiceRegionIncluded
        exclude = ["id", "ship_to_locations"]


class BaseShippingServiceRegionExcludedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ShippingServiceRegionExcluded
        exclude = ["id", "ship_to_locations"]


class BaseShippingServiceShipToLocationsSerializer(serializers.ModelSerializer):
    regionExcluded = BaseShippingServiceRegionExcludedSerializer(
        required=False, many=True
    )
    regionIncluded = BaseShippingServiceRegionIncludedSerializer(
        required=False, many=True
    )

    class Meta:
        model = models.ShippingServiceShipToLocations
        exclude = [
            "id",
            "shipping_service",
        ]


class BaseShippingCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ShippingCost
        exclude = ["id", "shipping_service"]


class BaseCashOnDeliveryFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CashOnDeliveryFee
        exclude = ["id", "shipping_service"]


class BaseAdditionalShippingCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AdditionalShippingCost
        exclude = ["id", "shipping_service"]


class BaseShippingServiceSerializer(serializers.ModelSerializer):
    additionalShippingCost = BaseAdditionalShippingCostSerializer(required=False)
    cashOnDeliveryFee = BaseCashOnDeliveryFeeSerializer(required=False)
    shippingCost = BaseShippingCostSerializer(required=False)
    shipToLocations = BaseShippingServiceShipToLocationsSerializer(required=False)
    surcharge = BaseSurchargeSerializer(required=False)

    class Meta:
        model = models.ShippingService
        exclude = ["id", "shipping_option"]


class BasePackageHandlingCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PackageHandlingCost
        exclude = ["id", "shipping_option"]


class BaseInsuranceFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InsuranceFee
        exclude = ["id", "shipping_option"]


class BaseShippingOptionSerializer(serializers.ModelSerializer):
    insuranceFee = BaseInsuranceFeeSerializer(required=False)
    packageHandlingCost = BasePackageHandlingCostSerializer(required=False)
    shippingServices = BaseShippingServiceSerializer(required=False, many=True)

    class Meta:
        model = models.ShippingOption
        exclude = ["id", "fulfillment_policy"]

    def validate(self, attrs):
        errors = dict()
        if attrs.get("insuranceOffered") and not attrs.get("insuranceFee"):
            errors.update(
                {
                    "insuranceFee": "Required if shippingOptions.insuranceOffered is set to true."
                }
            )
        if attrs.get("packageHandlingCost") and attrs.get("costType") != "CALCULATED":
            errors.update(
                {"packageHandlingCost": "Applicable to only CALCULATED shipping."}
            )
        if errors:
            raise ValidationError(errors)
        return attrs


class BaseHandlingTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.HandlingTime
        exclude = ["id", "fulfillment_policy"]


class BasePaymentPolicyCategoryTypeSerializer(AbstractCategoryTypeSerializer):
    class Meta(AbstractCategoryTypeSerializer.Meta):
        model = models.FulfillmentPolicyCategoryType


class BaseFulfillmentPolicySerializer(AbstractPolicySerializer):
    categoryTypes = BasePaymentPolicyCategoryTypeSerializer(
        required=False, many=True, allow_empty=False
    )
    handlingTime = BaseHandlingTimeSerializer(required=False)
    shippingOptions = BaseShippingOptionSerializer(required=False, many=True)
    shipToLocations = BaseFulfillmentPolicyShipToLocationsSerializer(required=False)

    class Meta(AbstractPolicySerializer.Meta):
        model = models.FulfillmentPolicy
        fields = AbstractPolicySerializer.Meta.fields + [
            "handlingTime",
            "shippingOptions",
            "shipToLocations",
        ]
