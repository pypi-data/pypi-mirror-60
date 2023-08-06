from ...base_api import EtsyAPI


class GetEtsyShippingTemplateList(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplate#method_findallusershippingprofiles
    """

    api_method_name = "findAllUserShippingProfiles"
    params = ["user_id"]


class GetEtsyShippingTemplate(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplate#method_getshippingtemplate
    """

    api_method_name = "getShippingTemplate"
    params = ["shipping_template_id"]


class DeleteEtsyShippingTemplate(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplate#method_deleteshippingtemplate
    """

    api_method_name = "deleteShippingTemplate"
    params = ["shipping_template_id"]


class CreateEtsyShippingTemplate(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplate#method_createshippingtemplate
    """

    api_method_name = "createShippingTemplate"
    params = [
        # body
        "title",
        "origin_country_id",
        "destination_country_id",
        "primary_cost",
        "secondary_cost",
        "destination_region_id",
        "min_processing_days",
        "max_processing_days",
    ]


class UpdateEtsyShippingTemplate(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplate#method_updateshippingtemplate
    """

    api_method_name = "updateShippingTemplate"
    params = [
        "shipping_template_id",
        # body
        "title",
        "origin_country_id",
        "min_processing_days",
        "max_processing_days",
    ]
