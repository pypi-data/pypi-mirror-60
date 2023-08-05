from etsy.api.etsy_action import EtsyAccountAction


class RemoteCreateEtsyShippingTemplateEntry(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplateentry#method_createshippingtemplateentry
    """

    api_method = "createShippingTemplateEntry"
    params = [
        "shipping_template_id",
        "destination_country_id",
        "primary_cost",
        "secondary_cost",
        "destination_region_id",
    ]


class RemoteGetEtsyShippingTemplateEntryList(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplate#method_findallshippingtemplateentries
    """

    api_method = "findAllShippingTemplateEntries"
    params = ["shipping_template_id"]


class RemoteGetEtsyShippingTemplateEntry(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplateentry#method_getshippingtemplateentry
    """

    api_method = "getShippingTemplateEntry"
    params = ["shipping_template_entry_id"]


class RemoteUpdateEtsyShippingTemplateEntry(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplateentry#method_updateshippingtemplateentry
    """

    api_method = "updateShippingTemplateEntry"
    params = [
        "shipping_template_entry_id",
        "destination_country_id",
        "primary_cost",
        "secondary_cost",
    ]


class RemoteDeleteEtsyShippingTemplateEntry(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplateentry#method_deleteshippingtemplateentry
    """

    api_method = "deleteShippingTemplateEntry"
    params = ["shipping_template_entry_id"]
