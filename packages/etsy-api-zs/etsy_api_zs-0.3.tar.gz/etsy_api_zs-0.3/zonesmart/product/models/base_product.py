from django.contrib.auth import get_user_model
from django.db import models

from model_utils.models import TimeStampedModel

from zonesmart.models import UUIDModel
from zonesmart.product.models.abstract import AbstractProduct

User = get_user_model()


class MarketplaceProductManager(models.Manager):
    def get_queryset(self):  # обобщить
        return (
            super().get_queryset().prefetch_related("ebay_products", "amazon_products")
        )

    # сделать generic-функции ($(marketplace_name) --> '$(marketplace_name)_products')
    def ebay(self):
        return super().get_queryset().prefetch_related("ebay_products")

    def amazon(self):
        return super().get_queryset().prefetch_related("amazon_products")


class BaseProduct(AbstractProduct, TimeStampedModel, UUIDModel):
    """
    Base product model.
    Required fields: user, title, sku, description, value, currency
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="base_products",
        related_query_name="base_product",
        verbose_name="Пользователь",
    )
    title = models.CharField(max_length=255, verbose_name="Title")

    objects = models.Manager()
    marketplace_products = MarketplaceProductManager()

    class Meta:
        verbose_name = "Базовый товар"
        verbose_name_plural = "Базовые товары"
