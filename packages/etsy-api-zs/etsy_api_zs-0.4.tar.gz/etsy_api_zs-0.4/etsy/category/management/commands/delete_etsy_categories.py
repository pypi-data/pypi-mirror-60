from django.core.management.base import BaseCommand

from etsy.category.models import EtsyCategoryTree

from zonesmart.utils.logger import get_logger

logger = get_logger(__name__)


class Command(BaseCommand):

    help = "Удаление категорий товаров Etsy"

    def handle(self, **options):
        num, _ = EtsyCategoryTree.objects.all().delete()
        logger.info(f"Все категории товаров Etsy удалены ({num}).")
