from django.db import models

from zonesmart.category.models import (
    AbstractMarketplaceCategory,
    AbstractMarketplaceCategoryTree,
)
from zonesmart.models import UUIDModel


class AmazonCategoryTree(AbstractMarketplaceCategoryTree):
    class Meta:
        verbose_name = "Дерево категорий для Amazon"
        verbose_name_plural = "Деревья категорий для Amazon"


class AmazonCategory(AbstractMarketplaceCategory):
    category_tree = models.ForeignKey(
        AmazonCategoryTree,
        on_delete=models.CASCADE,
        related_name="amazon_product_categories",
        verbose_name="Дерево категорий товаров Amazon",
    )

    class Meta:
        verbose_name = f"Категория товара Amazon"
        verbose_name_plural = f"Категории товара Amazon"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    # 'category_id',
                    "id_path",
                    "category_tree",
                ],
                name="unique_amazon_category_id_for_tree",
            )
        ]


class AmazonCategoryAspect(UUIDModel):
    category = models.ForeignKey(
        AmazonCategory,
        on_delete=models.CASCADE,
        related_name="aspects",
        verbose_name="Категория",
    )
    name = models.CharField(max_length=100, verbose_name="Название")
