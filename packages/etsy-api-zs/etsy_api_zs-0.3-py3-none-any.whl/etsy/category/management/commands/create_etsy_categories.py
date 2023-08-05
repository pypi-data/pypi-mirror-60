from django.core.management.base import BaseCommand

from etsy.category.actions import RemoteDownloadEtsyCategories

from zonesmart.utils.logger import get_logger

logger = get_logger(__name__)


class Command(BaseCommand):
    help = "Создание категорий товаров eBay"

    def handle(self, **options):
        RemoteDownloadEtsyCategories()()
