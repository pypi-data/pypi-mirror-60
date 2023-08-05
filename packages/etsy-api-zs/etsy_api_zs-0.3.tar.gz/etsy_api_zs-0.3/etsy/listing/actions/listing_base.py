from etsy.api.etsy_action import EtsyAccountAction, EtsyAction, EtsyEntityAction
from etsy.listing.models import EtsyListing


class EtsyListingAction(EtsyEntityAction):
    entity_model = EtsyListing
    entity_name = "listing"


class RemoteDeleteEtsyListing(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_deletelisting
    """

    api_method = "deleteListing"
    params = ["listing_id"]


class RemoteGetEtsyReceiptListings(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_findallreceiptlistings
    """

    api_method = "findAllReceiptListings"
    params = ["receipt_id"]


class RemoteGetEtsyShopSectionListings(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_findallshopsectionlistings
    """

    api_method = "findAllShopSectionListings"
    params = ["shop_id", "shop_section_id"]


class GetSuggestedStyles(EtsyAction):
    api_method = "findSuggestedStyles"
