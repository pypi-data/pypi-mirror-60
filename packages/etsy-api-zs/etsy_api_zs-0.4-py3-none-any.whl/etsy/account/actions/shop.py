from rest_framework.exceptions import ValidationError

from etsy.account.models import EtsyShop, EtsyShopSection
from etsy.account.serializers.shop.base import (
    EtsyShopSectionSerializer,
    BaseEtsyShopSerializer,
)
from etsy.api.etsy_action import EtsyAccountAction


# SHOP


class RemoteGetEtsyShopList(EtsyAccountAction):
    """
    https://www.etsy.com/developers/documentation/reference/shop#method_findallusershops
    """

    api_method = "findAllUserShops"
    params = ["user_id"]


class RemoteGetEtsyShop(EtsyAccountAction):
    """
    https://www.etsy.com/developers/documentation/reference/shop#method_getshop
    """

    api_method = "getShop"
    params = ["shop_id"]


class RemoteUpdateEtsyShop(EtsyAccountAction):
    """
    https://www.etsy.com/developers/documentation/reference/shop#method_updateshop
    """

    api_method = "updateShop"
    params = [
        "shop_id",
        # body
        "title",
    ]


class RemoteGetEtsyShopByListing(EtsyAccountAction):
    """
    https://www.etsy.com/developers/documentation/reference/shop#method_getlistingshop
    """

    api_method = "getListingShop"
    params = ["listing_id"]


# SHOP SECTION


class RemoteGetEtsyShopSectionList(EtsyAccountAction):
    """
    https://www.etsy.com/developers/documentation/reference/shopsection#method_findallshopsections
    """

    api_method = "findAllShopSections"
    params = ["shop_id"]


class RemoteGetEtsyShopSection(EtsyAccountAction):
    """
    https://www.etsy.com/developers/documentation/reference/shopsection#method_getshopsection
    """

    api_method = "getShopSection"
    params = ["shop_id", "shop_section_id"]


class RemoteCreateEtsyShopSection(EtsyAccountAction):
    """
    https://www.etsy.com/developers/documentation/reference/shopsection#method_createshopsection
    """

    api_method = "createShopSection"
    params = [
        "shop_id",
        # body
        "title",
    ]


class RemoteUpdateEtsyShopSection(EtsyAccountAction):
    """
    https://www.etsy.com/developers/documentation/reference/shopsection#method_updateshopsection
    """

    api_method = "updateShopSection"
    params = [
        "shop_id",
        "shop_section_id",
        # body
        "title",
    ]


class RemoteDeleteEtsyShopSection(EtsyAccountAction):
    """
    https://www.etsy.com/developers/documentation/reference/shopsection#method_deleteshopsection
    """

    api_method = "deleteShopSection"
    params = ["shop_id", "shop_section_id"]


# CUSTOM


class RemoteDownloadEtsyShopsAndSections(EtsyAccountAction):
    def get_shops(self):
        is_success, message, objects = self.raisable_action(RemoteGetEtsyShopList)
        return objects["results"]

    def get_shop_sections(self, shop_id: int):
        is_success, message, objects = self.raisable_action(
            RemoteGetEtsyShopSectionList, shop_id=shop_id
        )
        return objects["results"]

    def save_shop_and_sections(self, data):
        section_data_list = data.pop("sections")

        try:
            instance = EtsyShop.objects.get(shop_id=data["shop_id"])
        except EtsyShop.DoesNotExist:
            instance = None
        serializer = BaseEtsyShopSerializer(instance=instance, data=data)
        if serializer.is_valid(raise_exception=True):
            shop = serializer.save(channel=self.channel)

        for section_data in section_data_list:
            try:
                instance = EtsyShopSection.objects.get(
                    shop_section_id=section_data["shop_section_id"]
                )
            except EtsyShopSection.DoesNotExist:
                instance = None

            serializer = EtsyShopSectionSerializer(instance=instance, data=section_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(shop=shop)

    def make_request(self, **kwargs):
        shop_data_list = self.get_shops()
        assert len(shop_data_list) == 1, "WTF: more than 1 shop!"
        shop_data = shop_data_list[0]

        shop_sections_data = self.get_shop_sections(shop_id=shop_data["shop_id"])
        try:
            self.save_shop_and_sections(
                data={**shop_data, "sections": shop_sections_data}
            )
        except ValidationError as err:
            return False, str(err), {}

        return True, "", {}
