from ebay.location import actions as location_actions
from ebay.location.models import EbayLocation
from ebay.tests.base import EbayActionTest

from .factories import EbayLocationFactory


class EbayLocationTest(EbayActionTest):
    def get_locations(self, marketplace_user_account):
        return self.perform_action(
            action_class=location_actions.RemoteGetEbayLocations,
            marketplace_user_account=marketplace_user_account,
        )

    def download_locations(self, marketplace_user_account):
        return self.perform_action(
            action_class=location_actions.RemoteDownloadEbayLocations,
            marketplace_user_account=self.marketplace_user_account,
        )

    def upload_location(self, location):
        return self.perform_action(
            action_class=location_actions.RemoteUploadEbayLocation, entity=location,
        )

    def withdraw_location(self, location):
        return self.perform_action(
            action_class=location_actions.WithdrawEbayLocation, entity=location,
        )

    def test_get_locations(self):
        self.get_locations(marketplace_user_account=self.marketplace_user_account)

    def test_download_locations(self):
        is_success, message, objects = self.get_locations(
            marketplace_user_account=self.marketplace_user_account
        )

        if objects["results"]["total"] == 0:
            uploaded_locations = EbayLocationFactory.create_batch(size=3)
            for location in uploaded_locations:
                self.upload_location(location=location)
        else:
            uploaded_locations = None

        self.download_locations(marketplace_user_account=self.marketplace_user_account)
        loc_num1 = EbayLocation.objects.count()
        self.assertNotEqual(loc_num1, 0)

        self.download_locations(marketplace_user_account=self.marketplace_user_account)
        loc_num2 = EbayLocation.objects.count()
        self.assertNotEqual(loc_num2, 0)

        self.assertEqual(loc_num1, loc_num2)

        if uploaded_locations:
            for location in uploaded_locations:
                self.withdraw_location(location=location)

    def test_upload_and_withdraw_location(self):
        location = EbayLocationFactory.create(
            marketplace_user_account=self.marketplace_user_account,
        )
        self.upload_location(location=location)
        self.withdraw_location(location=location)
