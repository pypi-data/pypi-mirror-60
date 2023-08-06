from .base import CommerceAPI


class CatalogAPI(CommerceAPI):
    api_name = "catalog"
    api_version = "v1_beta"
    resource = "product"


class GetProduct(CatalogAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/commerce/catalog/resources/product/methods/getProduct
    """

    method_type = "GET"
    required_path_params = ["epid"]
