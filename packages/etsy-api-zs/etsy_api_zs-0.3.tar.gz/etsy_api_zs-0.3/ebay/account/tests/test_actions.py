from ebay.account import actions as account_actions
from ebay.category.actions import GetEbayDefaultCategoryTree
from ebay.location.actions import RemoteGetEbayLocations
from ebay.policy.actions import GetFulfillmentPolicyList
from ebay.tests.base import EbayActionTest


class EbayAccountsTest(EbayActionTest):
    app_action_class = GetEbayDefaultCategoryTree
    account_action_class = RemoteGetEbayLocations
    channel_action_class = GetFulfillmentPolicyList

    def test_app_action_without_channel(self):
        self.perform_action(
            action_class=self.app_action_class, marketplace_id=self.domain.code,
        )

    def test_app_action_with_channel(self):
        self.perform_action(
            action_class=self.app_action_class,
            channel=self.channel,
            marketplace_id=self.domain.code,
        )

    def test_channel_action_with_channel(self):
        self.perform_action(
            action_class=self.channel_action_class, channel=self.channel,
        )

    def test_channel_action_without_channel(self):
        with self.assertRaises(expected_exception=AttributeError):
            self.perform_action(
                action_class=self.channel_action_class, assert_success=False,
            )


class EbayUserAccountInfoTest(EbayActionTest):
    def test_get_account_info(self):
        self.perform_action(
            action_class=account_actions.GetEbayUserAccountInfo,
            marketplace_user_account=self.marketplace_user_account,
        )

    def test_get_account_privileges(self):
        self.perform_action(
            action_class=account_actions.GetEbayUserAccountPrivileges,
            marketplace_user_account=self.marketplace_user_account,
        )

    def test_get_user_account_rate_limits(self):
        self.perform_action(
            action_class=account_actions.GetEbayUserRateLimits,
            marketplace_user_account=self.marketplace_user_account,
        )

    def test_get_app_account_rate_limits(self):
        self.perform_action(
            action_class=account_actions.GetEbayAppRateLimits,
            marketplace_user_account=self.marketplace_user_account,
        )
