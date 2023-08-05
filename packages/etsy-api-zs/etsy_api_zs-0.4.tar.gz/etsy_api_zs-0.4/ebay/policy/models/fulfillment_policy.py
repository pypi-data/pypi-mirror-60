from django.core import validators
from django.db import models

from ebay.data import enums
from ebay.models import AbstractAmount
from ebay.policy.models import (
    AbstractCategoryType,
    AbstractPolicy,
    AbstractRegion,
    AbstractTimeDuration,
)
from model_utils import FieldTracker

from zonesmart.marketplace.models import Channel
from zonesmart.models import NestedUpdateOrCreateModelManager, UUIDModel


class FulfillmentPolicy(AbstractPolicy):
    REQUIRED_FOR_PUBLISHING_FIELDS = AbstractPolicy.REQUIRED_FOR_PUBLISHING_FIELDS + [
        "categoryTypes",
        "handlingTime",
        "shippingOptions",
    ]
    # Tracker should be added for each model that requires fields update tracking
    # https://github.com/jazzband/django-model-utils/issues/155
    tracker = FieldTracker()
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        limit_choices_to={"domain__marketplace__unique_name": "ebay"},
        related_name="fulfillment_policies",
        related_query_name="fulfillment_policy",
        verbose_name="Аккаунт пользователя eBay",
    )
    freightShipping = models.BooleanField(
        default=False, verbose_name="Продавец предлагает доставку"
    )
    globalShipping = models.BooleanField(
        default=False, verbose_name="Глобальная программа доставки"
    )
    localPickup = models.BooleanField(
        default=False, verbose_name="Продавец предлагает локальную доставку"
    )
    pickupDropOff = models.BooleanField(default=False, verbose_name="Click and Collect")

    objects = NestedUpdateOrCreateModelManager()

    class Meta:
        verbose_name = "Политика фулфилмента"
        verbose_name_plural = "Политики фулфилмента"
        default_related_name = "fulfillment_policy"


class FulfillmentPolicyCategoryType(AbstractCategoryType):
    fulfillment_policy = models.ForeignKey(
        FulfillmentPolicy, on_delete=models.CASCADE, related_name="categoryTypes"
    )

    class Meta:
        verbose_name = "Fulfillment policy category type"


class HandlingTime(AbstractTimeDuration):
    fulfillment_policy = models.OneToOneField(
        FulfillmentPolicy, on_delete=models.CASCADE, related_name="handlingTime"
    )
    unit = models.CharField(
        max_length=100, default="DAY", editable=False, verbose_name="Unit"
    )
    value = models.PositiveIntegerField(
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(30)],
        verbose_name="Value",
    )

    class Meta:
        verbose_name = "Fulfillment policy handling time"


class ShippingOption(UUIDModel):
    fulfillment_policy = models.ForeignKey(
        FulfillmentPolicy, on_delete=models.CASCADE, related_name="shippingOptions"
    )
    costType = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        choices=enums.ShippingCostTypeEnum,
        verbose_name="Cost type",
    )
    insuranceOffered = models.BooleanField(
        blank=True, null=True, verbose_name="Insurance offered"
    )
    optionType = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        choices=enums.ShippingOptionTypeEnum,
        verbose_name="Option type",
    )
    rateTableId = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Rate table id"
    )

    objects = NestedUpdateOrCreateModelManager()

    class Meta:
        verbose_name = "Fulfillment policy shipping option"


class InsuranceFee(AbstractAmount):
    shipping_option = models.OneToOneField(
        ShippingOption, on_delete=models.CASCADE, related_name="insuranceFee"
    )

    class Meta:
        verbose_name = "Shipping option insurance fee"


class PackageHandlingCost(AbstractAmount):
    shipping_option = models.OneToOneField(
        ShippingOption, on_delete=models.CASCADE, related_name="packageHandlingCost"
    )

    class Meta:
        verbose_name = "Shipping option package handling cost"


class ShippingService(UUIDModel):
    shipping_option = models.ForeignKey(
        ShippingOption, on_delete=models.CASCADE, related_name="shippingServices"
    )
    buyerResponsibleForPickup = models.BooleanField(
        default=False, verbose_name="Buyer responsible for pickup"
    )
    buyerResponsibleForShipping = models.BooleanField(
        default=False, verbose_name="Buyer responsible for shipping"
    )
    freeShipping = models.BooleanField(
        blank=True, null=True, verbose_name="Free shipping"
    )
    shippingCarrierCode = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        choices=enums.ShippingCarriersEnum,
        verbose_name="Shipping carrier code",
    )
    shippingServiceCode = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Shipping service code"
    )
    sortOrder = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[validators.MinValueValidator(1), validators.MaxValueValidator(5)],
        verbose_name="Sort order",
    )

    objects = NestedUpdateOrCreateModelManager()

    class Meta:
        verbose_name = "Shipping option shipping service"
        verbose_name_plural = "Shipping option shipping services"


class AdditionalShippingCost(AbstractAmount):
    shipping_service = models.OneToOneField(
        ShippingService, on_delete=models.CASCADE, related_name="additionalShippingCost"
    )

    class Meta:
        verbose_name = "Shipping service additional shipping cost"


class CashOnDeliveryFee(AbstractAmount):
    shipping_service = models.OneToOneField(
        ShippingService, on_delete=models.CASCADE, related_name="cashOnDeliveryFee"
    )

    class Meta:
        verbose_name = "Shipping service cash on delivery fee"


class ShippingCost(AbstractAmount):
    shipping_service = models.OneToOneField(
        ShippingService, on_delete=models.CASCADE, related_name="shippingCost"
    )

    class Meta:
        verbose_name = "Shipping service shipping cost"


class ShippingServiceShipToLocations(UUIDModel):
    shipping_service = models.OneToOneField(
        ShippingService,
        on_delete=models.CASCADE,
        related_name="shipToLocations",
        verbose_name="Shipping service",
    )

    objects = NestedUpdateOrCreateModelManager()

    class Meta:
        verbose_name = "Shipping service ship to locations"


class ShippingServiceRegionExcluded(AbstractRegion):
    ship_to_locations = models.ForeignKey(
        ShippingServiceShipToLocations,
        on_delete=models.CASCADE,
        related_name="regionExcluded",
    )

    class Meta:
        verbose_name = "Ship to locations region excluded"


class ShippingServiceRegionIncluded(AbstractRegion):
    ship_to_locations = models.ForeignKey(
        ShippingServiceShipToLocations,
        on_delete=models.CASCADE,
        related_name="regionIncluded",
    )

    class Meta:
        verbose_name = "Ship to locations region included"


class Surcharge(AbstractAmount):
    shipping_service = models.OneToOneField(
        ShippingService, on_delete=models.CASCADE, related_name="surcharge"
    )

    class Meta:
        verbose_name = "Shipping service surcharge"


class FulfillmentPolicyShipToLocations(UUIDModel):
    fulfillment_policy = models.OneToOneField(
        FulfillmentPolicy,
        on_delete=models.CASCADE,
        related_name="shipToLocations",
        verbose_name="Fulfillment policy",
    )

    objects = NestedUpdateOrCreateModelManager()

    class Meta:
        verbose_name = "Fulfillment policy ship to locations"


class FulfillmentPolicyRegionExcluded(AbstractRegion):
    ship_to_locations = models.ForeignKey(
        FulfillmentPolicyShipToLocations,
        on_delete=models.CASCADE,
        related_name="regionExcluded",
    )

    class Meta:
        verbose_name = "Fulfillment policy region excluded"


class FulfillmentPolicyRegionIncluded(AbstractRegion):
    ship_to_locations = models.ForeignKey(
        FulfillmentPolicyShipToLocations,
        on_delete=models.CASCADE,
        related_name="regionIncluded",
    )

    class Meta:
        verbose_name = "Fulfillment policy region included"
