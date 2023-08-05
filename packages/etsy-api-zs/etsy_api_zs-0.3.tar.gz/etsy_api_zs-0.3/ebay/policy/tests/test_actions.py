from ebay.policy import actions as policy_actions

# from ebay.policy import models as policy_models
from ebay.tests.base import EbayActionTest


class EbayPolicyTest(EbayActionTest):
    def test_get_fulfillment_policies(self):
        self.perform_action(
            action_class=policy_actions.GetFulfillmentPolicyList, channel=self.channel,
        )

    def test_get_payment_policies(self):
        self.perform_action(
            action_class=policy_actions.GetPaymentPolicyList, channel=self.channel,
        )

    def test_get_return_policies(self):
        self.perform_action(
            action_class=policy_actions.GetReturnPolicyList, channel=self.channel,
        )

    # def test_download_policies(self, **kwargs):
    #     action_classes = [
    #         policy_actions.RemoteDownloadFulfillmentPolicyList,
    #         policy_actions.RemoteDownloadPaymentPolicyList,
    #         policy_actions.RemoteDownloadReturnPolicyList,
    #     ]
    #     model_classes = [
    #         policy_models.FulfillmentPolicy,
    #         policy_models.PaymentPolicy,
    #         policy_models.ReturnPolicy,
    #     ]
    #     for action_class, model_class in zip(action_classes, model_classes):
    #         counts = []
    #         for _ in range(2):
    #             self.perform_action(
    #                 action_class=action_class,
    #                 channel=self.channel
    #             )
    #             counts.append(model_class.objects.count())
    #         self.assertEqual(counts[0], counts[1])
