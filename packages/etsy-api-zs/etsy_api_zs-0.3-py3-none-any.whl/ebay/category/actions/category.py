from ebay.api.ebay_action import EbayAction
from ebay.category.models import EbayCategory, EbayCategoryTree
from ebay_api.commerce.taxonomy import GetCategoryTree

from zonesmart.category.actions import DownloadMarketplaceCategories

from .base import logger


class GetEbayDomainCategories(EbayAction):
    description = "Получение категорий домена eBay."
    api_class = GetCategoryTree


class RemoteDownloadEbayDomainCategories(
    GetEbayDomainCategories, DownloadMarketplaceCategories
):
    description = "Получение и сохранение категорий домена eBay."

    def _get_category_tree(self, category_tree_id, **kwargs):
        return EbayCategoryTree.objects.get(category_tree_id=category_tree_id)

    def _get_root_node(self, objects):
        return objects["results"]["rootCategoryNode"]

    def _get_categories(self, category_tree, node, parent_name_path=""):
        categories = []
        for child_node in node["childCategoryTreeNodes"]:
            name = child_node["category"]["categoryName"]
            name_path = (
                " / ".join([parent_name_path, name]) if parent_name_path else name
            )
            is_leaf = child_node.get("leafCategoryTreeNode", False)

            if not is_leaf:
                categories += self._get_categories(
                    category_tree=category_tree,
                    node=child_node,
                    parent_name_path=name_path,
                )

            category = EbayCategory(
                category_tree=category_tree,
                category_id=child_node["category"]["categoryId"],
                parent_id=node["category"]["categoryId"],
                level=child_node["categoryTreeNodeLevel"],
                name=name,
                name_path=name_path,
                is_leaf=is_leaf,
            )
            categories.append(category)

        return categories

    def success_trigger(
        self, message: str, objects: dict, category_tree_id: str, **kwargs
    ):
        if str(category_tree_id) != objects["results"]["categoryTreeId"]:
            message = (
                f"ID запрошенного и полученного деревьев категорий eBay не совпадают: "
                f"{category_tree_id} != {objects['results']['categoryTreeId']}"
            )
            return super().failure_trigger(message, objects, **kwargs)

        kwargs["category_tree_id"] = category_tree_id
        return super().success_trigger(message=message, objects=objects, **kwargs)


class RemoteDownloadEbayCategories:
    description = "Получение и сохранение категорий для нескольких доменов eBay."

    def __call__(self, domain_codes=[]):
        action = RemoteDownloadEbayDomainCategories()
        category_tree_list = EbayCategoryTree.objects.all()
        if domain_codes:
            category_tree_list = category_tree_list.filter(
                domain__code__in=domain_codes
            )

        updated_trees = []
        not_updated_trees = []
        for category_tree in category_tree_list:
            is_success, message, objects = action(
                category_tree_id=category_tree.category_tree_id
            )
            if is_success:
                logger.info(
                    f'Категории для домена "{category_tree.domain.code}" обновлены.'
                )
                updated_trees.append(category_tree.id)
            else:
                logger.error(
                    f'Не удалось обновить категории для домена "{category_tree.domain.code}".'
                )
                not_updated_trees.append(category_tree.id)

        logger.info(
            f"Обновлённые деревья категорий eBay: {updated_trees}.\n"
            f"Не обновлённые деревья категорий eBay: {not_updated_trees}."
        )
        return updated_trees, not_updated_trees
