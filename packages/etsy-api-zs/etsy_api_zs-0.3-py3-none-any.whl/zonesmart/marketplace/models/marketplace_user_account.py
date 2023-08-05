from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from zonesmart.marketplace.models import Marketplace
from zonesmart.models import UUIDModel

User = get_user_model()


class MarketplaceUserAccount(UUIDModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="marketplace_accounts",
        related_query_name="marketplace_account",
        verbose_name="Пользователь",
    )
    marketplace = models.ForeignKey(
        Marketplace,
        on_delete=models.CASCADE,
        related_name="marketplace_user_accounts",
        related_query_name="marketplace_user_account",
        verbose_name="Маркетплейс",
    )

    class Meta:
        verbose_name = "Аккаунт маркетплейса"
        verbose_name_plural = "Аккаунты маркетплейсов"

    def __str__(self):
        return f"Аккаунт пользователя {self.user} для {self.marketplace.name}"

    @property
    def marketplace_account(self):
        try:
            if self.marketplace in Marketplace.amazon.all():
                return self.amazon_user_account
            else:
                return getattr(self, f"{self.marketplace.unique_name}_user_account")
        except (ObjectDoesNotExist, AttributeError):
            raise ObjectDoesNotExist(
                f"Пользователь не создал аккаунт для маркетплейса {self.marketplace}"
            )

        raise AttributeError(
            f'У пользователя "{self.user}" нет аккаунта маркетплейса "{self.marketplace}".'
        )
