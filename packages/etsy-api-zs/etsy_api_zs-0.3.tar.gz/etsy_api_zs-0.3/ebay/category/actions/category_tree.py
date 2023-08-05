import json

from django.core.cache import cache

from ebay.api.ebay_action import EbayAction, EbayActionError
from ebay.category.models import EbayCategoryTree
from ebay_api.commerce import taxonomy as category_tree_api

from zonesmart.marketplace.models import Domain

from .base import logger


class GetEbayDefaultCategoryTree(EbayAction):
    description = "Получение ID дефолтного для домена eBay дерева категорий товаров."
    api_class = category_tree_api.GetDefaultCategoryTreeId


class RemoteDownloadEbayDefaultCategoryTree(GetEbayDefaultCategoryTree):
    description = (
        "Получение и сохранение ID дефолтного для домена eBay дерева категорий товаров."
    )

    def success_trigger(self, message: str, objects: dict, marketplace_id: str):
        category_tree_id = objects["results"]["categoryTreeId"]
        category_tree_version = objects["results"]["categoryTreeVersion"]

        try:
            domain = Domain.objects.get(code=marketplace_id)
        except Domain.DoesNotExist:
            message = (
                f"Домена {marketplace_id} нет в базе данных.\n"
                f"Дерево для домена {marketplace_id} не создано."
            )
            return super().failure_trigger(message, objects)
        else:
            category_tree, created = EbayCategoryTree.objects.update_or_create(
                domain=domain, category_tree_id=category_tree_id,
            )
            if created:
                message = f'Дерево категорий для домена "{domain.code}" создано."'
            else:
                message = f'Дерево категорий для домена "{domain.code}" обновлено."'

                if category_tree_version != category_tree.category_tree_version:
                    objects["tree_version_updated"] = True
                    objects["tree_id"] = category_tree.id
                    objects["tree_old_version"] = category_tree.category_tree_version
                else:
                    objects["tree_version_updated"] = False

            category_tree.category_tree_version = category_tree_version
            category_tree.save()

        return super().success_trigger(message=message, objects=objects)


class RemoteDownloadEbayDefaultCategoryTreeList:
    description = "Получение и сохранение ID дефолтных деревьев категорий товаров eBay."

    supported_domain_codes = [
        "EBAY_US",
        "EBAY_DE",
        "EBAY_GB",
        "EBAY_FR",
        "EBAY_RU",
        "EBAY_AU",
        "EBAY_AT",
        "EBAY_CA",
        "EBAY_HK",
        "EBAY_IN",
        "EBAY_IE",
        "EBAY_IT",
        "EBAY_MY",
        "EBAY_NL",
        "EBAY_PH",
        "EBAY_PL",
        "EBAY_SG",
        "EBAY_ES",
        "EBAY_CH",
    ]

    @staticmethod
    def _restore_tree_versions(updated_trees):
        for tree_data in updated_trees:
            EbayCategoryTree.objects.filter(id=tree_data["tree_id"]).update(
                category_tree_version=tree_data["tree_old_version"]
            )

    def __call__(self, domain_codes=[]):
        if domain_codes:
            domain_codes = set(self.supported_domain_codes) & set(domain_codes)
        else:
            available_domain_codes_set = set(
                domain.code for domain in Domain.objects.all()
            )
            domain_codes = set(self.supported_domain_codes) & available_domain_codes_set

        action = RemoteDownloadEbayDefaultCategoryTree()
        updated_trees = []
        for domain_code in domain_codes:
            logger.info(f'Получение дерева категорий для домена "{domain_code}".')
            is_success, message, objects = action(marketplace_id=domain_code)
            if is_success:
                if objects.get("tree_version_updated", False):
                    updated_trees.append(
                        {
                            "tree_id": objects["tree_id"],
                            "tree_old_version": objects["tree_old_version"],
                        }
                    )
            else:
                cache_key = "ebay_category_trees_old_versions"
                cache.set(cache_key, json.dumps(updated_trees), timeout=86400)
                try:
                    self._restore_tree_versions(updated_trees)
                except Exception as error:
                    raise error
                else:
                    cache.expire(cache_key, timeout=0)

                raise EbayActionError(message)

        logger.info(
            f"Деревья категорий eBay, версии которых обновились: {updated_trees}."
        )
        return updated_trees
