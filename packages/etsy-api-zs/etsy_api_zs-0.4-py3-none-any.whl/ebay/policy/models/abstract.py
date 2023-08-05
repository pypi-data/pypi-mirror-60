from django.db import models

from ebay.data.enums import CategoryTypeEnum, TimeDurationUnitEnum

from zonesmart.data.enums import CurrencyCodeEnum
from zonesmart.marketplace.models import MarketplaceEntity
from zonesmart.models import UUIDModel


class AbstractPolicy(MarketplaceEntity):
    REQUIRED_FOR_PUBLISHING_FIELDS = [
        "name",
    ]
    TRACKER_EXCLUDE_FIELDS = MarketplaceEntity.TRACKER_EXCLUDE_FIELDS + ["policy_id"]
    name = models.CharField(max_length=64, verbose_name="Name")
    description = models.CharField(
        max_length=250, blank=True, null=True, verbose_name="Description"
    )
    policy_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Уникальный ID политики в системе eBay",
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class AbstractTimeDuration(UUIDModel):
    unit = models.CharField(
        max_length=100, choices=TimeDurationUnitEnum, verbose_name="Unit"
    )
    value = models.PositiveIntegerField(verbose_name="Value")

    class Meta:
        abstract = True


class AbstractCategoryType(UUIDModel):
    default = models.BooleanField(default=False, verbose_name="Default")
    name = models.CharField(
        max_length=29, choices=CategoryTypeEnum, verbose_name="Name"
    )

    class Meta:
        abstract = True


class AbstractPolicyAmount(UUIDModel):
    currency = models.CharField(
        max_length=20, choices=CurrencyCodeEnum, verbose_name="Currency"
    )
    value = models.FloatField(verbose_name="Value")

    class Meta:
        abstract = True
