from django.db import models

from model_utils import Choices
from model_utils.models import StatusModel, TimeStampedModel

from zonesmart.models import UUIDModel
from zonesmart.users.models import User


class SupportRequest(StatusModel, TimeStampedModel, UUIDModel):
    STATUS = Choices(
        ("NEW", "Ожидает рассмотрения"),
        ("WAITING_FOR_HELPER", "Ожидает ответа оператора"),
        ("WAITING_FOR_USER", "Ожидает ответа пользователя"),
        ("CLOSED_BY_USER", "Закрыта пользователем"),
        ("CLOSED_BY_TIMEOUT", "Закрыта по истечению времени"),
    )
    # Fields
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="support_requests",
        verbose_name="Создатель",
    )
    helper = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Оператор поддержки",
    )
    title = models.CharField(max_length=100, verbose_name="Тема заявки")

    def __str__(self):
        return f"Заявка (ID: {self.id})"

    class Meta:
        verbose_name = "Заявка в службу поддержки"
        verbose_name_plural = "Заявки в службу поддержки"
