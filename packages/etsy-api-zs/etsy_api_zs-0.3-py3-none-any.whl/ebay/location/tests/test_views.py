from ebay.location.models import EbayLocation
from ebay.location.tests.factories import EbayLocationFactory
from ebay.tests.factories import EbayMarketplaceUserAccountFactory
from rest_framework import status

from zonesmart.tests.base import BaseViewSetTest


class EbayLocationViewSetTest(BaseViewSetTest):
    url_path = "ebay:location:location"

    def get_ebay_location_list(self):
        url = self.get_url(postfix="list")
        return self.make_request(method="GET", url_path=url)

    def get_ebay_location(self, location_id):
        url = self.get_url(postfix="detail", id=location_id)
        return self.make_request(method="GET", url_path=url)

    def create_ebay_location(self, data):
        url = self.get_url(postfix="list")
        return self.make_request(method="POST", url_path=url, data=data)

    def delete_ebay_location(self, location_id):
        url = self.get_url(postfix="detail", id=location_id)
        return self.make_request(method="DELETE", url_path=url)

    def update_ebay_location(self, location_id, data):
        url = self.get_url(postfix="detail", id=location_id)
        return self.make_request(method="PUT", url_path=url, data=data)

    def partial_update_ebay_location(self, location_id, data):
        url = self.get_url(postfix="detail", id=location_id)
        return self.make_request(method="PATCH", url_path=url, data=data)

    def download_ebay_location_list(self, marketplace_user_account):
        url = self.get_url(
            postfix="download-from-ebay",
            marketplace_user_account=marketplace_user_account,
        )
        return self.make_request(method="GET", url_path=url)

    def upload_ebay_location(self, location_id):
        url = self.get_url(postfix="upload-to-ebay", id=location_id)
        return self.make_request(method="POST", url_path=url)

    def test_get_ebay_location_list(self):
        EbayLocationFactory.create_batch(size=3)

        response = self.get_ebay_location_list()
        self.assertStatus(response)

        self.assertEqual(EbayLocation.objects.count(), response.json()["count"])

    def test_get_ebay_location(self):
        location = EbayLocationFactory.create()

        response = self.get_ebay_location(location_id=location.id)
        self.assertStatus(response)

        self.assertEqual(str(location.id), response.json()["id"])

    def test_create_ebay_location(self):
        location = EbayLocationFactory.create()
        location.delete()

        marketplace_user_account = EbayMarketplaceUserAccountFactory.create()
        data = self.obj_factory_to_dict(EbayLocationFactory)
        data.update({"marketplace_user_account": marketplace_user_account.id})

        response = self.create_ebay_location(data=data)
        self.assertStatus(response, status=status.HTTP_201_CREATED)

        self.assertEqual(
            EbayLocation.objects.filter(
                merchantLocationKey=data["merchantLocationKey"]
            ).count(),
            1,
        )

    def test_delete_ebay_location(self):
        location = EbayLocationFactory.create()

        response = self.delete_ebay_location(location_id=location.id)
        self.assertStatus(response, status=status.HTTP_204_NO_CONTENT)

        self.assertEqual(EbayLocation.objects.filter(id=location.id).count(), 0)

    def test_update_ebay_location(self):
        location = EbayLocationFactory.create(
            name="to be updated",
            addressLine1="to be the same",
            addressLine2="to be deleted",
        )
        update_data = {
            "marketplace_user_account": location.marketplace_user_account.id,
            "countryCode": location.countryCode,
            "name": "updated name",
            "addressLine2": None,
        }
        partial_update_data = {
            "name": "updated name",
            "addressLine2": None,
        }
        method_list = [self.update_ebay_location, self.partial_update_ebay_location]
        data_list = [update_data, partial_update_data]
        for method, data in zip(method_list, data_list):
            response = method(location_id=location.id, data=data)
            self.assertStatus(response, status=status.HTTP_200_OK)

            updated_location = EbayLocation.objects.get(id=location.id)
            self.assertNotEqual(updated_location.name, location.name)
            self.assertEqual(updated_location.addressLine1, location.addressLine1)
            self.assertIsNone(updated_location.addressLine2)
