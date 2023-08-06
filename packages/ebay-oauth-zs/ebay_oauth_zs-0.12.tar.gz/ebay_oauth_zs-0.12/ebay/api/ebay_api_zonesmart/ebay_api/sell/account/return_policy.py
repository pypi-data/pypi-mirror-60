from .base import AccountAPI


class ReturnPolicyAPI(AccountAPI):
    resource = "return_policy"


class CreateReturnPolicy(ReturnPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/return_policy/methods/createReturnPolicy
    """

    method_type = "POST"


class DeleteReturnPolicy(ReturnPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/return_policy/methods/deleteReturnPolicy
    """

    method_type = "DELETE"
    required_path_params = ["return_policy_id"]


class GetReturnPolicy(ReturnPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/return_policy/methods/getReturnPolicy
    """

    method_type = "GET"
    required_path_params = ["return_policy_id"]


class GetReturnPolicies(ReturnPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/return_policy/methods/getReturnPolicies
    """

    method_type = "GET"
    required_query_params = ["marketplace_id"]


class GetReturnPolicyByName(ReturnPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/return_policy/methods/getReturnPolicyByName
    """

    method_type = "GET"
    url_postfix = "get_by_policy_name"
    required_query_params = ["marketplace_id", "name"]


class UpdateReturnPolicy(ReturnPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/return_policy/methods/updateReturnPolicy
    """

    method_type = "PUT"
    required_path_params = ["return_policy_id"]
