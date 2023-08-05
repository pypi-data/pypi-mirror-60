from ebay.api.ebay_action import EbayAccountAction
from ebay.listing.actions.base import EbayListingAction
from ebay.listing.actions.listing_delete import (
    RemoteDeleteEbayListing,
    RemoteDeleteEbayProduct,
    RemoteDeleteEbayProductGroup,
)
from ebay.listing.serializers.listing.remote_api.listing import EbayListingSerializer
from ebay_api.sell.inventory import item, item_group, offer

# ITEM ACTIONS


class RemoteCreateEbayItemList(EbayAccountAction):
    api_class = item.BulkCreateOrReplaceInventoryItem


# OFFER ACTIONS


class RemoteCreateEbayOffer(EbayAccountAction):
    api_class = offer.CreateOffer


class PublishEbayOffer(EbayAccountAction):
    api_class = offer.PublishOffer


class WithdrawEbayOffer(EbayAccountAction):
    api_class = offer.WithdrawOffer


class RemoteUpdateEbayOffer(EbayListingAction):
    api_class = offer.UpdateOffer

    def get_path_params(self, product, **kwargs):
        if not product.offerId:
            message = (
                "Товар не может быть обновлён на eBay, так как не был туда загружен."
            )
            raise self.exception_class(message)

        kwargs["offerId"] = product.offerId
        return super().get_path_params(**kwargs)


# GROUP ACTIONS


class PublishEbayProductGroup(EbayAccountAction):
    api_class = item_group.PublishOfferByInventoryItemGroup


class RemoteCreateEbayProductGroup(EbayListingAction):
    api_class = item_group.CreateOrReplaceInventoryItemGroup

    def get_path_params(self, **kwargs):
        kwargs["inventoryItemGroupKey"] = self.listing.listing_sku
        return super().get_path_params(**kwargs)


class RemoteUpdateEbayProductGroup(EbayListingAction):
    api_class = item_group.UpdateInventoryItemGroup

    def get_path_params(self, **kwargs):
        kwargs["inventoryItemGroupKey"] = self.listing.listing_sku
        return super().get_path_params(**kwargs)


# MAIN ACTION


class SyncEbayListing(EbayListingAction):

    # ITEM

    def remote_create_or_update_items(self, **kwargs):
        return self.raisable_action(api_class=RemoteCreateEbayItemList, **kwargs)

    def remote_delete_item(self, **kwargs):
        return self.raisable_action(api_class=RemoteDeleteEbayProduct, **kwargs)

    # OFFER

    def remote_create_offer(self, **kwargs):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteCreateEbayOffer, **kwargs
        )
        return objects["results"]["offerId"]

    def remote_update_offer(self, **kwargs):
        return self.raisable_action(api_class=RemoteUpdateEbayOffer, **kwargs)

    def publish_offer(self, **kwargs):
        is_success, message, objects = self.raisable_action(
            api_class=PublishEbayOffer, **kwargs
        )
        return objects["results"]["listingId"]

    def withdraw_offer(self, **kwargs):
        return self.raisable_action(api_class=WithdrawEbayOffer, **kwargs)

    def remote_create_or_update_offer(self, offer_data: dict, product=None):
        if not product:
            # get product by offer sku
            product = self.listing.products.get(sku=offer_data["sku"])

        # # check if the only offer is created on ebay
        if product.offerId:
            # update the only offer on ebay
            self.remote_update_offer(payload=offer_data, product=product)
            created = False
            data = {}
        else:
            # create the only offer on ebay
            offerId = self.remote_create_offer(payload=offer_data, product=product)
            created = True
            data = {"offerId": offerId}

        # try:
        #     # create the only offer on ebay
        #     offerId = self.remote_create_offer(payload=offer_data, product=product)
        #     created = True
        #     data = {'offerId': offerId}
        # except self.exception_class:
        #     # update the only offer on ebay
        #     self.remote_update_offer(payload=offer_data, product=product)
        #     created = False
        #     data = {}

        if created:
            # check if the only offer is published
            if product.listingId:
                raise self.exception_class(
                    "Оффер значится опубликованным, хотя не был создан на eBay."
                )

        return created, data

    # GROUP

    def remote_create_or_update_product_group(self, **kwargs):
        return self.raisable_action(api_class=RemoteCreateEbayProductGroup, **kwargs)

    def remote_delete_product_group(self, **kwargs):
        return self.raisable_action(api_class=RemoteDeleteEbayProductGroup, **kwargs)

    def remote_update_product_group(self, **kwargs):
        return self.raisable_action(api_class=RemoteUpdateEbayProductGroup, **kwargs)

    def publish_product_group(self, **kwargs):
        is_success, message, objects = self.raisable_action(
            api_class=PublishEbayProductGroup, **kwargs
        )
        return objects["results"]["listingId"]

    # LISTING

    def remote_delete_ebay_listing(self, **kwargs):
        action = RemoteDeleteEbayListing(instance=self)
        return action(**kwargs)

    # GENERAL

    def remove_soft_deleted_products(self):
        # delete from ebay locally soft deleted products
        deleted_products = self.listing.products.soft_deleted()
        for product in deleted_products:
            self.remote_delete_item(product=product)
        # full remove of soft deleted products
        deleted_products.delete()

    def remote_create_or_update_single_listing(self, listing_data):
        # check if the listing is published as a multiple listing
        if self.listing.groupListingId:
            # delete product group from ebay
            self.remote_delete_product_group()

        # update or create the only offer
        offer_data = listing_data["offers"]["requests"][0]
        # get the only product of the listing
        product = self.listing.products.get(sku=offer_data["sku"])

        # create or update the only offer
        created, data = self.remote_create_or_update_offer(
            offer_data=offer_data, product=product
        )

        # check if offer was created
        if created:
            # save offerId
            product.offerId = data["offerId"]
            product.save()

        # check if the only offer is not published
        if not product.listingId:
            # publish offer
            listingId = self.publish_offer(offerId=product.offerId)
            # save listingId
            product.listingId = listingId
            product.save()

    def remote_create_or_update_multiple_listing(self, listing_data):
        # create or update offers
        for offer_data in listing_data["offers"]["requests"]:
            # get product by offer sku
            product = self.listing.products.get(sku=offer_data["sku"])
            # create or update an offer
            created, data = self.remote_create_or_update_offer(
                offer_data=offer_data, product=product
            )
            # check if offer is published
            if created:
                # save offerId
                product.offerId = data["offerId"]
                product.save()
            elif product.listingId:
                # withdraw offer
                self.withdraw_offer(offerId=product.offerId)

        # create or update product group on ebay
        self.remote_create_or_update_product_group(
            payload=listing_data["group"]["create"]
        )

        # check if the listing is not published
        if not self.listing.published:
            # publish product group
            listingId = self.publish_product_group(
                payload=listing_data["group"]["publish"]
            )
            # save listingId
            self.listing.groupListingId = listingId
            self.listing.save()

    def make_request(self, **kwargs):
        # get data
        listing_data = EbayListingSerializer(self.listing).data

        try:
            # remove soft deleted products locally and from ebay
            self.remove_soft_deleted_products()

            if self.listing.products_num:
                # create or update items on ebay
                self.remote_create_or_update_items(payload=listing_data["items"])

                if self.listing.products_num == 1:
                    # single listing case
                    self.remote_create_or_update_single_listing(
                        listing_data=listing_data
                    )
                elif self.listing.products_num > 1:
                    # multiple listing case
                    self.remote_create_or_update_multiple_listing(
                        listing_data=listing_data
                    )

                # save the listing as published
                self.listing.published = True
                self.listing.save()
            else:
                if self.listing.published:
                    self.remote_delete_ebay_listing()

        except self.exception_class as error:
            is_success = False
            message = f"Не удалось сихронизировать листинг с eBay (SKU: {self.listing.sku}).\n{error}"
            objects = {}

        else:
            is_success = True
            message = (
                f"Листинг был успешно сихронизирован с eBay (SKU: {self.listing.sku})."
            )
            objects = {}

        return is_success, message, objects
