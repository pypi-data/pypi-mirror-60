from django.db import models

from zonesmart.models import UUIDModel


class Announcement(UUIDModel):
    published = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=300)

    class Meta:
        verbose_name = "Анонс"
        verbose_name_plural = "Анонсы"
        ordering = ["published"]
