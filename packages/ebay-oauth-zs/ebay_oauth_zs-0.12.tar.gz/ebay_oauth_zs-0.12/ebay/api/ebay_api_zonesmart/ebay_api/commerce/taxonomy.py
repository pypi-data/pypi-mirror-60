from .base import CommerceAPI


class TaxonomyAPI(CommerceAPI):
    api_name = "taxonomy"
    api_version = "v1_beta"
    resource = "category_tree"
    method_type = "GET"

    @property
    def headers(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Encoding": "application/gzip",
        }
        return headers


class GetDefaultCategoryTreeId(TaxonomyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/commerce/taxonomy/resources/category_tree/methods/getDefaultCategoryTreeId
    """

    resource = ""
    url_postfix = "get_default_category_tree_id"
    required_query_params = ["marketplace_id"]


class CategoryTreeAPI(TaxonomyAPI):
    required_path_params = ["category_tree_id"]


class GetCategoryTree(CategoryTreeAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/commerce/taxonomy/resources/category_tree/methods/getCategoryTree
    """


class GetCategorySubtree(CategoryTreeAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/commerce/taxonomy/resources/category_tree/methods/getCategorySubtree
    """

    url_postfix = "get_category_subtree"
    required_query_params = ["category_id"]


class GetCategorySuggestions(CategoryTreeAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/commerce/taxonomy/resources/category_tree/methods/getCategorySuggestions
    """

    url_postfix = "get_category_suggestions"
    required_query_params = ["q"]


class GetItemAspectsForCategory(CategoryTreeAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/commerce/taxonomy/resources/category_tree/methods/getItemAspectsForCategory
    """

    url_postfix = "get_item_aspects_for_category"
    required_query_params = ["category_id"]
