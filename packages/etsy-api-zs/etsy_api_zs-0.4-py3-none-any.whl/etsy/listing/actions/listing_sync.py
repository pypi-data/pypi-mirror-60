from etsy.api.etsy_action import EtsyAccountAction


class RemoteCreateEtsySingleListing(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_createlisting
    """

    api_method = "createListing"
    params = [
        # body
        # required
        "quantity",
        "title",
        "description",
        "price",
        "who_made",
        "is_supply",
        "when_made",
        # optional
        "materials",
        "shipping_template_id",
        "shop_section_id",
        "image_ids",
        "image",
        "state",
        "taxonomy_id",
    ]


class RemoteUpdateEtsySingleListing(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_updatelisting
    """

    api_method = "updateListing"
    params = [
        "listing_id",
        # body
        "title",
        "description",
        "materials",
        "renew",
        "shipping_template_id",
        "shop_section_id",
        "image_ids",
        "state",
        "taxonomy_id",
        "who_made",
        "is_supply",
        "when_made",
    ]


class RemoteUpdateEtsyListingInventory(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listinginventory#method_updateinventory
    """

    api_method = "updateInventory"
    params = [
        "listing_id",
        # body
        "products",
        "price_on_property",
        "quantity_on_property",
        "sku_on_property",
    ]
