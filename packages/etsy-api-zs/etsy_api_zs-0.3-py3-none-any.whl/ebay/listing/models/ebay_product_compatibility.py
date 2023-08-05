from django.db import models

from ebay.listing.models import AbstractEbayAspect
from ebay.listing.models.ebay_listing import EbayListing

from zonesmart.marketplace.models import MarketplaceEntity
from zonesmart.models import NestedUpdateOrCreateModelManager


class EbayProductCompatibilityManager(NestedUpdateOrCreateModelManager):
    RELATED_OBJECT_NAMES = ["properties"]
    UPDATE_OR_CREATE_FILTER_FIELDS = {"properties": ["name"]}


class EbayProductCompatibility(MarketplaceEntity):
    listing = models.ForeignKey(
        EbayListing,
        on_delete=models.CASCADE,
        related_name="compatibilities",
        related_query_name="compatibility",
        verbose_name="Листинг",
        limit_choices_to={
            "channel__domain__code__in": [
                "EBAY_MOTORS_US",
                "EBAY_US",
                "EBAY_CA",
                "EBAY_GB",
                "EBAY_DE",
                "EBAY_AU",
                "EBAY_FR",
                "EBAY_IT",
                "EBAY_ES",
            ],
        },
    )
    notes = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="Комментарии"
    )
    # Product Identifier
    epid = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="ePID транспорта"
    )
    ktype = models.CharField(  # only for DE, UK and AU sites
        max_length=50, blank=True, null=True, verbose_name="K Type Number транспорта"
    )

    objects = EbayProductCompatibilityManager()

    def __str__(self):
        return f"Транспорт (ID: {self.id}), совместимый с листингом (ID: {self.listing.id})"

    class Meta:
        verbose_name = "Совместимый с деталью транспорт"
        verbose_name_plural = "Совместимый с деталью транспорт"


class EbayProductCompatibilityProperty(AbstractEbayAspect):
    compatibility = models.ForeignKey(
        EbayProductCompatibility,
        on_delete=models.CASCADE,
        related_name="properties",
        related_query_name="property",
        verbose_name="Совместимый товар",
    )
