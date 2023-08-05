from django.db import IntegrityError
from django.test import TestCase

from zonesmart.marketplace.models import Channel
from zonesmart.marketplace.tests import factories


class ChannelModelTest(TestCase):
    def setUp(self) -> None:
        self.channel = factories.ChannelFactory.create()

    def test_unique_channel_constraint(self):
        """
        Test for checking the unique constraint of the model in 2 fields: user & channel
        """
        with self.assertRaisesRegexp(IntegrityError, "unique_domain"):
            Channel.objects.create(
                marketplace_user_account=self.channel.marketplace_user_account,
                domain=self.channel.domain,
            )

    def test_domain_property(self):
        """
        Test for checking the existence of a domain property in a model
        """
        self.assertTrue(hasattr(self.channel, "domain"))

    def test_marketplace_user_account_property(self):
        """
        Test for checking the existence of a marketplace property in a model
        """
        self.assertTrue(hasattr(self.channel, "marketplace_user_account"))
