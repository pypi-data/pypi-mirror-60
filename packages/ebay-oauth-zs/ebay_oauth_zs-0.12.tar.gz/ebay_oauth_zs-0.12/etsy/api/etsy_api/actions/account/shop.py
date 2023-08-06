from ...base_api import EtsyAPI


class GetEtsyShopList(EtsyAPI):
    """
    https://www.etsy.com/developers/documentation/reference/shop#method_findallusershops
    """

    api_method_name = "findAllUserShops"
    params = ["user_id"]


class GetEtsyShop(EtsyAPI):
    """
    https://www.etsy.com/developers/documentation/reference/shop#method_getshop
    """

    api_method_name = "getShop"
    params = ["shop_id"]


class UpdateEtsyShop(EtsyAPI):
    """
    https://www.etsy.com/developers/documentation/reference/shop#method_updateshop
    """

    api_method_name = "updateShop"
    params = [
        "shop_id",
        # body
        "title",
    ]


class GetEtsyShopByListing(EtsyAPI):
    """
    https://www.etsy.com/developers/documentation/reference/shop#method_getlistingshop
    """

    api_method_name = "getListingShop"
    params = ["listing_id"]
