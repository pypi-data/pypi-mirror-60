from ebay.api.ebay_action import EbayAction
from ebay.category.models import EbayCategory, EbayCategoryTree
from ebay_api.sell.metadata.marketplace import GetListingStructurePolicies


class GetVariationsSupportedCategories(EbayAction):
    description = "Получение допустимых категорий для групп товаров домена eBay."
    api_class = GetListingStructurePolicies


class MarkVariationsSupportedEbayDomainCategories(GetVariationsSupportedCategories):
    description = "Обновление поля variationsSupported категорий домена eBay."

    def success_trigger(
        self, message: str, objects: dict, marketplace_id: str, **kwargs
    ):
        variations_supported_categories = [
            obj["categoryId"]
            for obj in objects["results"]["listingStructurePolicies"]
            if obj.get("variationsSupported", False)
        ]

        # filter categories by domain
        categories = EbayCategory.objects.filter(
            category_tree__domain__code=marketplace_id,
        )
        # set all categories as not supporting variations
        categories.update(variationsSupported=False)
        # update variations supporting categories
        categories.filter(category_id__in=variations_supported_categories).update(
            variationsSupported=True
        )

        message = (
            f"Данные о доступности категорий для вариаций товаров домена {marketplace_id} "
            f"успешно загружены ({len(variations_supported_categories)} объектов)."
        )
        return super().success_trigger(message=message, objects=objects)


class MarkVariationsSupportedCategories:
    description = "Получение и сохранение допустимых категорий для групп товаров eBay."

    def __call__(self):
        action = MarkVariationsSupportedEbayDomainCategories()
        for category_tree in EbayCategoryTree.objects.all():
            is_success, message, obj = action(marketplace_id=category_tree.domain.code)
