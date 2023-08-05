from ebay.listing.models import EbayListing
from ebay.order import actions as order_actions
from ebay.order.models import EbayOrder
from ebay.tests.base import EbayActionTest


class EbayOrderTest(EbayActionTest):
    def delete_orders(self):
        EbayOrder.objects.all().delete()

    def download_orders(self, marketplace_user_account, filter_by_user_products):
        return self.perform_action(
            action_class=order_actions.RemoteDownloadEbayOrders,
            marketplace_user_account=marketplace_user_account,
            filter_by_user_products=filter_by_user_products,
        )

    def test_get_orders(self):
        self.perform_action(
            action_class=order_actions.RemoteGetEbayOrders,
            marketplace_user_account=self.marketplace_user_account,
        )

    def test_download_orders(self):
        for filter_by_user_products in [False]:  # , True]:
            self.delete_orders()
            is_success, message, objects = self.download_orders(
                marketplace_user_account=self.marketplace_user_account,
                filter_by_user_products=filter_by_user_products,
            )
            self.assertEqual(
                EbayOrder.objects.count(),
                EbayOrder.objects.filter(
                    marketplace_user_account=self.marketplace_user_account,
                ).count(),
            )

            if len(objects["results"].get("saved_orders", [])):
                self.assertNotEqual(EbayOrder.objects.count(), 0)
                if filter_by_user_products:
                    for order_id in objects["results"]["saved_orders"]:
                        order = EbayOrder.objects.get(id=order_id)
                        products_num = 0
                        for line_item in order.line_items.all():
                            products_num += EbayListing.objects.filter(
                                sku=line_item.sku
                            ).count()
                        self.assertNotEqual(products_num, 0)
