from abc import abstractmethod

from django.db.models import Q

from bulk_sync import bulk_sync

from zonesmart.marketplace.api.marketplace_action import MarketplaceAction


class DownloadMarketplaceCategories(MarketplaceAction):
    @abstractmethod
    def _get_category_tree(self, *args, **kwargs):
        pass

    @abstractmethod
    def _get_root_node(self, objects: dict):
        pass

    @abstractmethod
    def _get_categories(self, category_tree, node, **kwargs):
        pass

    def _sync_categories(
        self, category_tree, categories, filters=None, key_fields=None
    ):
        if not filters:
            filters = Q(category_tree=category_tree)
        if not key_fields:
            key_fields = ["category_tree_id", "category_id"]

        results = bulk_sync(
            new_models=categories,
            filters=filters,
            key_fields=key_fields,
            batch_size=1000,
        )

        message = (
            f'Категории для домена "{category_tree.domain.code}" успешно загружены ({len(categories)} объектов).\n'
            "Результаты: {created} создано, {updated} обновлено, {deleted} удалено.".format(
                **results["stats"]
            )
        )
        return results, message

    def success_trigger(self, message: str, objects: dict, **kwargs):
        category_tree = self._get_category_tree(**kwargs)

        categories = self._get_categories(
            category_tree=category_tree, node=self._get_root_node(objects=objects),
        )

        results, message = self._sync_categories(
            category_tree=category_tree, categories=categories
        )
        objects["results"] = results

        return super().success_trigger(message=message, objects=objects)
