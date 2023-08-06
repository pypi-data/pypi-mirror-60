from ...base_api import EtsyAPI


class GetEtsyUserAccountInfo(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/user#method_getuser
    """

    api_method_name = "getUser"
    params = ["user_id"]
