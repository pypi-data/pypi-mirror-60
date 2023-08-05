from django.db import models

from zonesmart.models import UUIDModel
from zonesmart.support.models import SupportRequestMessage
from zonesmart.utils.upload import get_support_file_upload_path


class SupportRequestMessageFile(UUIDModel):
    support_request_message = models.ForeignKey(
        SupportRequestMessage,
        on_delete=models.CASCADE,
        related_name="files",
        related_query_name="file",
        verbose_name="Заявка",
    )
    file = models.FileField(
        upload_to=get_support_file_upload_path, verbose_name="Приложенный файл"
    )

    class Meta:
        verbose_name = "Приложенный к сообщению файл"
        verbose_name_plural = "Приложенные к сообщению файлы"
