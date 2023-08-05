from django.core.management.base import BaseCommand

from amazon.category.models import AmazonCategoryTree

from zonesmart.marketplace.models import Domain
from zonesmart.utils.logger import get_logger

logger = get_logger(__name__)


class Command(BaseCommand):
    help = "Удаление категорий товаров Amazon"

    def add_arguments(self, parser):
        parser.add_argument(
            "domain_name", help="Домен Amazon, категории которого будут удалены."
        )

    def handle(self, **options):
        domain_name = options.get("domain_name", None)
        trees = AmazonCategoryTree.objects.all()
        if domain_name:
            try:
                domain = Domain.objects.get(name=domain_name)
                trees.get(domain=domain).delete()
            except Domain.DoesNotExist:
                logger.warning(f'Домен с именем "{domain_name}" не найден.')
            except AmazonCategoryTree.DoesNotExist:
                logger.warning(
                    f'Дерево категорий для домена с именем "{domain_name}" не найдено.'
                )
            else:
                logger.info(f'Все категории удалены для домена "{domain_name}".')
        else:
            trees.delete()
            logger.info("Все категории удалены для всех доменов.")
