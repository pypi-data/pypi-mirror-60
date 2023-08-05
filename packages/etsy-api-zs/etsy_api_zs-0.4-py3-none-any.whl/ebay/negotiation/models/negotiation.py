from django.db import models

from ebay.listing.models import EbayListing
from ebay.models.abstract import AbstractDuration, AbstractNonConvertedAmount

from zonesmart.models import UUIDModel


class EbayEligibleItem(UUIDModel):
    ebay_product = models.OneToOneField(
        EbayListing,
        on_delete=models.CASCADE,
        related_name="eligible_item",
        verbose_name="Товар eBay",
    )
    active = models.BooleanField(
        blank=True, default=False, verbose_name="Интерес к товару активен",
    )

    @property
    def listingId(self):
        return self.ebay_product.listingId

    class Meta:
        verbose_name = "Товар, к которому проявили интерес"
        verbose_name_plural = "Товары, к которым проявили интерес"


class EbayBuyerOffer(UUIDModel):
    allowCounterOffer = models.BooleanField(  # "True" value is not supported
        default=False, editable=False, verbose_name="Контр-предложения разрешены",
    )
    message = models.TextField(
        max_length=2000, blank=True, null=True, verbose_name="Сообщение покупателям",
    )

    class Meta:
        verbose_name = "Предложение покупателям"
        verbose_name_plural = "Предложения покупателям"


class EbayBuyerOfferDuration(AbstractDuration):  # 2 Days ONLY
    offer = models.OneToOneField(
        EbayBuyerOffer,
        on_delete=models.CASCADE,
        related_name="duration",
        verbose_name="Предложение покупателям",
    )

    class Meta:
        verbose_name = "Продолжительность действия предложения"
        verbose_name_plural = verbose_name


class EbayBuyerOfferedItem(
    UUIDModel
):  # offeredItems container is currently supporting only one item
    offer = models.ForeignKey(
        EbayBuyerOffer,
        on_delete=models.CASCADE,
        related_name="offered_items",
        related_query_name="offered_item",
        verbose_name="Предложение покупателю",
    )
    # Fields
    eligibleItem = models.OneToOneField(
        EbayEligibleItem, on_delete=models.CASCADE, verbose_name="Желаемый товар",
    )
    # listingId = models.CharField(
    #     max_length=30, verbose_name='ID листинга',
    # )
    discountPercentage = models.FloatField(
        blank=True, null=True, verbose_name="Скидка в процентах",
    )
    quantity = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Количество товаров, требуемое для скидки",
    )

    class Meta:
        verbose_name = "Предлагаемый товар"
        verbose_name_plural = "Предлагаемые товары"


class EbayBuyerOfferPrice(
    AbstractNonConvertedAmount
):  # price can't be set together with discountPercentage
    offered_item = models.OneToOneField(
        EbayBuyerOfferedItem,
        on_delete=models.CASCADE,
        related_name="price",
        verbose_name="Предлагаемый товар",
    )

    class Meta:
        verbose_name = "Цена для предложения покупателю"
        verbose_name_plural = verbose_name
