from etsy.api.etsy_action import EtsyAccountAction


# BASE


class RemoteGetEtsyShopActiveListings(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_findallshoplistingsactive
    """

    api_method = "findAllShopListingsActive"
    params = ["shop_id"]


class RemoteGetEtsyShopInactiveListings(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_findallshoplistingsinactive
    """

    api_method = "findAllShopListingsInactive"
    params = ["shop_id"]


class RemoteGetEtsyShopDraftListings(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_findallshoplistingsdraft
    """

    api_method = "findAllShopListingsDraft"
    params = ["shop_id"]


class RemoteGetEtsyShopExpiredListings(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_findallshoplistingsexpired
    """

    api_method = "findAllShopListingsExpired"
    params = ["shop_id"]


class RemoteGetEtsySingleListing(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_getlisting
    """

    api_method = "getListing"
    params = ["listing_id"]


class RemoteGetEtsyListingProductList(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listinginventory#method_getinventory
    """

    api_method = "getInventory"
    params = ["listing_id"]


class RemoteGetEtsyProduct(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listingproduct#method_getproduct
    """

    api_method = "getProduct"
    params = ["listing_id", "product_id"]


class RemoteGetEtsyOffering(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listingoffering#method_getoffering
    """

    api_method = "getOffering"
    params = ["listing_id", "product_id", "offering_id"]


class RemoteGetEtsyListingAttibuteList(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/propertyvalue#method_getattributes
    """

    api_method = "getAttributes"
    params = ["listing_id"]


class RemoteGetEtsyListingAttibute(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/propertyvalue#method_getattribute
    """

    api_method = "getAttribute"
    params = ["listing_id", "property_id"]


class RemoteCreateOrUpdateEtsyListingAttibute(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/propertyvalue#method_updateattribute
    """

    api_method = "updateAttribute"
    params = [
        "listing_id",
        "property_id",
        # body
        "value_ids",
        "values",
        "scale_id",
    ]


class RemoteDeleteEtsyListingAttibute(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/propertyvalue#method_deleteattribute
    """

    api_method = "deleteAttribute"
    params = ["listing_id", "property_id"]


# CUSTOM


class RemoteGetEtsySingleListingList(EtsyAccountAction):
    def get_expired_listings(self):
        is_success, message, objects = self.raisable_action(
            RemoteGetEtsyShopExpiredListings
        )
        return objects["results"]

    def get_draft_listings(self):
        is_success, message, objects = self.raisable_action(
            RemoteGetEtsyShopDraftListings
        )
        return objects["results"]

    def get_inactive_listings(self):
        is_success, message, objects = self.raisable_action(
            RemoteGetEtsyShopInactiveListings
        )
        return objects["results"]

    def get_active_listings(self):
        is_success, message, objects = self.raisable_action(
            RemoteGetEtsyShopActiveListings
        )
        return objects["results"]

    def make_request(self, **kwargs):
        try:
            results = [
                *self.get_expired_listings(),
                *self.get_draft_listings(),
                *self.get_inactive_listings(),
                *self.get_active_listings(),
            ]
        except self.exception_class as error:
            is_success = False
            errors = str(error)
            message = f"Не удалось получить листинги Etsy.\n{errors}"
            objects = {"errors": errors}
        else:
            is_success = True
            message = "Все листинги Etsy успешно получены."
            objects = {
                "count": len(results),
                "results": results,
            }
        return is_success, message, objects


class RemoteGetEtsyListingList(RemoteGetEtsySingleListingList):
    def get_listing_attributes(self, listing_id: int):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEtsyListingAttibuteList, listing_id=listing_id,
        )
        return {"attributes": objects["results"]}

    def get_listing_products(self, listing_id: int):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEtsyListingProductList, listing_id=listing_id,
        )
        return objects["results"]

    def success_trigger(self, message, objects, **kwargs):
        updated_results = []
        for listing_data in objects["results"]:
            products_data = self.get_listing_products(
                listing_id=listing_data["listing_id"]
            )
            attributes_data = self.get_listing_attributes(
                listing_id=listing_data["listing_id"]
            )
            updated_results.append({**listing_data, **products_data, **attributes_data})
        objects["results"] = updated_results
        return super().success_trigger(message, objects, **kwargs)


class RemoteDownloadEtsyListingList(RemoteGetEtsyListingList):
    def success_trigger(self, **kwargs):
        is_success, message, objects = super().success_trigger(**kwargs)
        # TODO
        return is_success, message, objects


class RemoteGetEtsyListing(EtsyAccountAction):
    def get_single_listing(self, listing_id: int):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEtsySingleListing, listing_id=listing_id,
        )
        return objects["results"]

    def get_listing_attributes(self, listing_id: int):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEtsyListingAttibuteList, listing_id=listing_id,
        )
        return {"attributes": objects["results"]}

    def get_listing_products(self, listing_id: int):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEtsyListingProductList, listing_id=listing_id,
        )
        return objects["results"]

    def make_request(self, listing_id: int, **kwargs):
        try:
            listing_data = self.get_single_listing(listing_id=listing_id)
            products_data = self.get_listing_products(listing_id=listing_id)
            attributes_data = self.get_listing_attributes(listing_id=listing_id)
        except self.exception_class as error:
            is_success = False
            errors = str(error)
            message = f"Не удалось получить листинг Etsy.\n{errors}"
            objects = {"errors": errors}
        else:
            is_success = True
            message = "Листинг Etsy и его вариации успешно получены."
            objects = {"results": {**listing_data, **products_data, **attributes_data}}
        return is_success, message, objects


class RemoteDownloadEtsyListing(RemoteGetEtsyListing):
    def success_trigger(self, **kwargs):
        is_success, message, objects = super().success_trigger(**kwargs)
        # TODO
        return is_success, message, objects
