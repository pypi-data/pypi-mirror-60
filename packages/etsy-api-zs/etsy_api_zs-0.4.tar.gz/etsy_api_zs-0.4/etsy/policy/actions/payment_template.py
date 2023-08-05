from etsy.api.etsy_action import EtsyAccountAction


class RemoteGetEtsyPaymentTemplateList(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/paymenttemplate#method_findalluserpaymenttemplates
    """

    api_method = "findAllUserPaymentTemplates"
    params = ["user_id"]


class RemoteCreateEtsyPaymentTemplate(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/paymenttemplate#method_createshoppaymenttemplate
    """

    api_method = "createShopPaymentTemplate"
    params = [
        "shop_id",
        # body
        "allow_check",
        "allow_mo",
        "allow_other",
        "allow_paypal",
        "allow_cc",
        "paypal_email",
        "name",
        "first_line",
        "second_line",
        "city",
        "state",
        "zip",
        "country_id",
    ]


class RemoteUpdateEtsyPaymentTemplate(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/paymenttemplate#method_updateshoppaymenttemplate
    """

    api_method = "updateShopPaymentTemplate"
    params = [
        "shop_id",
        "payment_template_id",
        # body
        "allow_check",
        "allow_mo",
        "allow_other",
        "allow_paypal",
        "allow_cc",
        "paypal_email",
        "name",
        "first_line",
        "second_line",
        "city",
        "state",
        "zip",
        "country_id",
    ]
