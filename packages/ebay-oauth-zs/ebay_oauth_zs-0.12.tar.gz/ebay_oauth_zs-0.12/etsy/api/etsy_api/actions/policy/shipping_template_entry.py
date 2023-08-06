from ...base_api import EtsyAPI


class CreateEtsyShippingTemplateEntry(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplateentry#method_createshippingtemplateentry
    """

    api_method_name = "createShippingTemplateEntry"
    params = [
        "shipping_template_id",
        "destination_country_id",
        "primary_cost",
        "secondary_cost",
        "destination_region_id",
    ]


class GetEtsyShippingTemplateEntryList(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplate#method_findallshippingtemplateentries
    """

    api_method_name = "findAllShippingTemplateEntries"
    params = ["shipping_template_id"]


class GetEtsyShippingTemplateEntry(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplateentry#method_getshippingtemplateentry
    """

    api_method_name = "getShippingTemplateEntry"
    params = ["shipping_template_entry_id"]


class UpdateEtsyShippingTemplateEntry(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplateentry#method_updateshippingtemplateentry
    """

    api_method_name = "updateShippingTemplateEntry"
    params = [
        "shipping_template_entry_id",
        "destination_country_id",
        "primary_cost",
        "secondary_cost",
    ]


class DeleteEtsyShippingTemplateEntry(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplateentry#method_deleteshippingtemplateentry
    """

    api_method_name = "deleteShippingTemplateEntry"
    params = ["shipping_template_entry_id"]
