from ..base import SellAPI


class AccountAPI(SellAPI):
    api_name = "account"


class GetPrivileges(AccountAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/privilege/methods/getPrivileges
    """

    resource = "privilege"
    method_type = "GET"
