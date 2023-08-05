from amazon.order import actions as order_actions
from amazon.order.models import AmazonOrder
from amazon.tests.base import AmazonActionTest


class AmazonOrderTest(AmazonActionTest):
    def delete_orders(self):
        AmazonOrder.objects.all().delete()

    def download_orders(self, channel):
        return self.perform_action(
            action_class=order_actions.DownloadAmazonOrders, channel=channel,
        )

    def test_get_orders(self):
        self.perform_action(
            action_class=order_actions.GetAmazonOrders, channel=self.channel,
        )

    def test_download_orders(self):
        self.delete_orders()
        is_success, message, objects = self.download_orders(channel=self.channel)
        self.assertEqual(
            AmazonOrder.objects.count(),
            AmazonOrder.objects.filter(channel=self.channel).count(),
        )
        if len(objects["results"]):
            self.assertNotEqual(AmazonOrder.objects.count(), 0)

    def test_download_filtered_orders(self):
        self.delete_orders()
        is_success, message, objects = self.download_orders(channel=self.channel)
        self.assertEqual(
            AmazonOrder.objects.count(),
            AmazonOrder.objects.filter(channel=self.channel).count(),
        )
