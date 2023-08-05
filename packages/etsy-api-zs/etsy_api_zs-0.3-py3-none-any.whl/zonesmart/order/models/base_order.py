from django.contrib.auth import get_user_model
from django.db import models

from model_utils.managers import InheritanceManager

User = get_user_model()


class BaseOrder(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="base_orders",
        related_query_name="base_order",
        verbose_name="Пользователь",
    )

    objects = InheritanceManager()
