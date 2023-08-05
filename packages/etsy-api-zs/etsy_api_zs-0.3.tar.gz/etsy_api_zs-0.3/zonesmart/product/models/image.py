import os
from tempfile import NamedTemporaryFile
from urllib.error import URLError
from urllib.request import urlopen

from django.core.files import File
from django.db import models

from zonesmart.models import UUIDModel
from zonesmart.utils.logger import get_logger
from zonesmart.utils.upload import get_product_image_upload_path

logger = get_logger(app_name=__file__)


class ProductImage(UUIDModel):
    image_file = models.ImageField(
        null=True,
        upload_to=get_product_image_upload_path,
        verbose_name="Файл изображения",
    )
    image_url = models.URLField(blank=True, null=True, verbose_name="URL изображения")
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание изображения"
    )

    def __str__(self):
        if self.image_file and getattr(self.image_file, "url", None):
            name = os.path.basename(self.image_file.url)
        else:
            name = getattr(self, "image_url", "файл отсутствует")
        return f"Изображение товара (ID: {self.id}, file: {name})"

    class Meta:
        verbose_name = "Фото товара"
        verbose_name_plural = "Фото товара"

    def save_file_by_url(self, url):
        img_temp = NamedTemporaryFile(delete=True)
        try:
            img_temp.write(urlopen(url).read())
            img_temp.flush()
        except URLError:
            logger.warning(f"Не удалось загрузить изображение по url {url}")
            return False
        else:
            self.image_url = url
            self.image_file.save(f"image_{self.pk}", File(img_temp))
            self.save()
            return True

    def get_url(self) -> str:
        return self.image_url or self.image_file.url

    def get_name(self):
        return self.get_url().split("/")[-1]
