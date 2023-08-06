from ..base_api import EtsyAPI


class GetEtsyCategoryTreeVersion(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/taxonomy#method_getsellertaxonomyversion
    """

    description = "Получение версии дерева категорий товаров Etsy"
    api_method_name = "getSellerTaxonomyVersion"


class GetEtsyCategories(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/taxonomy#method_getsellertaxonomy
    """

    description = "Получение категорий товаров Etsy"
    api_method_name = "getSellerTaxonomy"


class GetEtsyCategoryAspects(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/taxonomynodeproperty#method_gettaxonomynodeproperties
    """

    api_method_name = "getTaxonomyNodeProperties"
    params = ["taxonomy_id"]
