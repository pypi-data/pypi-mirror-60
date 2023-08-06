from amazon.category.models import AmazonCategory, AmazonCategoryTree
from amazon.report.actions import GetReport, RequestReport

from zonesmart.category.actions import DownloadMarketplaceCategories
from zonesmart.marketplace.models import Domain
from zonesmart.utils.logger import get_logger

logger = get_logger(__name__)


class RequestBrowseTreeReport(RequestReport):
    def make_request(self, domain_code: str, **query_params):
        query_params["MarketplaceId"] = domain_code
        query_params["report_type"] = "_GET_XML_BROWSE_TREE_DATA_"
        return super().make_request(**query_params)


class GetAmazonCategories(GetReport):
    def make_request(self, domain_code: str, *args, **kwargs):
        kwargs["report_type"] = "_GET_XML_BROWSE_TREE_DATA_"
        return super().make_request(*args, **kwargs)

    def success_trigger(self, message: str, objects: dict, domain_code: str, **kwargs):
        logger.info(f'Категории для канала продаж "{domain_code}" успешно получены.')
        kwargs["domain_code"] = domain_code
        return super().success_trigger(message, objects, **kwargs)


class RemoteDownloadAmazonCategories(
    GetAmazonCategories, DownloadMarketplaceCategories
):
    def _get_category_tree(self, domain_code, **kwargs):
        domain = Domain.objects.get(code=domain_code)
        category_tree, created = AmazonCategoryTree.objects.get_or_create(domain=domain)
        return category_tree

    def _get_root_node(self, objects):
        return objects["results"]

    def _get_categories(self, category_tree, node):
        categories = []
        for category_data in node:
            category_id = category_data["browseNodeId"]

            name = category_data["browseNodeStoreContextName"]
            if not name:
                if category_data["browsePathByName"]:
                    name = category_data["browsePathByName"].split(",")[-1]
                else:
                    name = category_data["browseNodeName"]

            name_path = category_data["browsePathByName"]
            if not name_path:
                name_path = name

            level = len(name_path.split(","))
            id_path = category_data["browsePathById"]
            if level == 1:
                parent_id = "0"
            else:
                parent_id = id_path.split(",")[-2]

            is_leaf = category_data["hasChildren"] == "true"

            category = AmazonCategory(
                category_tree=category_tree,
                category_id=category_id,
                parent_id=parent_id,
                level=level,
                name=name,
                name_path=name_path,
                id_path=id_path,
                is_leaf=is_leaf,
            )
            categories.append(category)

        return categories

    def _sync_categories(self, *args, **kwargs):
        kwargs["key_fields"] = ["category_tree_id", "id_path"]
        return super()._sync_categories(*args, **kwargs)
