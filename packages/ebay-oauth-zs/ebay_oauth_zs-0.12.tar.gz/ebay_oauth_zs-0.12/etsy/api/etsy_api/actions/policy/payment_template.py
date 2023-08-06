from ...base_api import EtsyAPI


class GetEtsyPaymentTemplateList(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/paymenttemplate#method_findalluserpaymenttemplates
    """

    api_method_name = "findAllUserPaymentTemplates"
    params = ["user_id"]


class GetEtsyPaymentTemplateListForShop(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/paymenttemplate#section_methods
    """

    api_method_name = "findShopPaymentTemplates"
    params = ["shop_id"]


class CreateEtsyPaymentTemplate(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/paymenttemplate#method_createshoppaymenttemplate
    """

    api_method_name = "createShopPaymentTemplate"
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


class UpdateEtsyPaymentTemplate(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/paymenttemplate#method_updateshoppaymenttemplate
    """

    api_method_name = "updateShopPaymentTemplate"
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
