from django.contrib.auth import get_user_model
from django.db import models

from zonesmart.marketplace.models import Domain, MarketplaceUserAccount
from zonesmart.models import UUIDModel

User = get_user_model()


class Channel(UUIDModel):
    marketplace_user_account = models.ForeignKey(
        MarketplaceUserAccount,
        on_delete=models.CASCADE,
        related_name="channels",
        related_query_name="channel",
        verbose_name="Маркетлейс аккаунт пользователя",
    )
    name = models.CharField(max_length=80, verbose_name="Название канала продаж")
    domain = models.ForeignKey(  # добавить проверку, что domain.marketplace == marketplace_user_account.marketplace
        Domain,
        on_delete=models.CASCADE,
        related_name="channels",
        related_query_name="channel",
        verbose_name="Домен",
    )

    class Meta:
        verbose_name = "Канал продаж пользователя"
        verbose_name_plural = "Каналы продаж пользователей"
        constraints = [
            models.UniqueConstraint(
                fields=["marketplace_user_account", "domain"], name="unique_domain"
            )
        ]

    def __str__(self):
        return self.name
