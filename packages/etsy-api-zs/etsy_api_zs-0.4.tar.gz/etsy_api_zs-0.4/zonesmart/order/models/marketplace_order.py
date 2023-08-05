from django.db import models

from zonesmart.marketplace.models import Channel
from zonesmart.order.models import BaseOrder


class MarketplaceOrder(BaseOrder):
    channel = models.OneToOneField(
        Channel,
        on_delete=models.CASCADE,
        related_name="marketplace_orders",
        related_query_name="marketplace_order",
        verbose_name="Пользовательский канал продаж",
    )

    class Meta:
        verbose_name = "Заказ пользователя для канала продаж"
        verbose_name_plural = "Заказы пользователей для каналов продаж"
