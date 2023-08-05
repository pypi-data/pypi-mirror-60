from django.db import models

from ebay.data import enums

from zonesmart.models import UUIDModel


class AbstractRegion(UUIDModel):
    regionName = models.CharField(max_length=255, verbose_name="Region name")
    regionType = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        choices=enums.RegionTypeEnum,
        verbose_name="Region type",
    )

    class Meta:
        abstract = True
