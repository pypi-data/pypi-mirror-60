from django.db import models

from zonesmart.marketplace.models import Channel
from zonesmart.models import UUIDModel


class EtsyShop(UUIDModel):
    # https://www.etsy.com/developers/documentation/reference/shop
    channel = models.OneToOneField(
        Channel,
        on_delete=models.CASCADE,
        limit_choices_to={"domain__marketplace__unique_name": "etsy"},
        related_name="shop",
        verbose_name="Пользовательский канал продаж",
    )
    # Fields
    shop_id = models.CharField(
        max_length=30, unique=True, verbose_name="ID магазина Etsy"
    )
    title = models.CharField(
        max_length=300, verbose_name="Заголовок на главной странице магазина",
    )
    # announcement = models.CharField(
    #     max_length=500,
    #     verbose_name='Объявление на домашней странице магазина',
    # )
    # policy_welcome
    # policy_payment
    # policy_shipping
    # policy_refunds
    # policy_additional
    # policy_seller_info
    # policy_privacy
    is_vacation = models.BooleanField(
        blank=True, default=False, verbose_name="Магазин временно не работает",
    )
    listing_active_count = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Количество активных листингов",
    )
    url = models.URLField(blank=True, null=True, verbose_name="URL магазина",)

    def __str__(self):
        return f"{self.title[:50]} (ID: {self.shop_id})"

    class Meta:
        verbose_name = "Магазин Etsy"
        verbose_name_plural = "Магазины Etsy"


class EtsyShopSection(UUIDModel):
    # https://www.etsy.com/developers/documentation/reference/shopsection
    shop = models.ForeignKey(
        EtsyShop,
        on_delete=models.CASCADE,
        related_name="sections",
        related_query_name="section",
        verbose_name="Магазин Etsy",
    )
    # Fields
    shop_section_id = models.CharField(
        max_length=30, unique=True, verbose_name="ID секции магазина Etsy"
    )
    title = models.CharField(max_length=300, verbose_name="Заголовок секции магазина",)
    active_listing_count = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Количество активных листингов в секции",
    )

    def __str__(self):
        return f"{self.title[:50]} (ID: {self.shop_section_id})"

    class Meta:
        verbose_name = "Секция магазина Etsy"
        verbose_name_plural = "Секции магазина Etsy"
