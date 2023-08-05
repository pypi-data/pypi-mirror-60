from django.conf import settings

from ebay.account.tests.factories import (
    EbaySandboxUserAccountFactory,
    EbayUserAccountFactory,
)
from ebay.tests.factories import EbayChannelFactory

from zonesmart.tests.base import BaseActionTest, BaseTest, BaseViewSetTest


class EbayTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.channel = EbayChannelFactory.create()
        self.domain = self.channel.domain
        self.marketplace_user_account = self.channel.marketplace_user_account

        if settings.EBAY_SANDBOX:
            account_factory = EbaySandboxUserAccountFactory
        else:
            account_factory = EbayUserAccountFactory
        self.user_account = account_factory.create(
            marketplace_user_account=self.marketplace_user_account,
        )


class EbayViewSetTest(EbayTest, BaseViewSetTest):
    pass


class EbayActionTest(EbayTest, BaseActionTest):
    def perform_action(self, *args, **kwargs):
        kwargs["retry_if_500"] = True
        return super().perform_action(*args, **kwargs)
