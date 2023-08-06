from etsy.category.models import EtsyCategory, EtsyCategoryTree
from etsy.api.etsy_action import EtsyAction
from etsy.api.etsy_api.actions.category import (
    GetEtsyCategories,
    GetEtsyCategoryTreeVersion,
    GetEtsyCategoryAspects,
)

from zonesmart.category.actions import DownloadMarketplaceCategories
from zonesmart.marketplace.models import Domain
from zonesmart.utils.logger import get_logger

logger = get_logger("etsy_category_actions")


class RemoteGetEtsyCategoryAspects(EtsyAction):
    api_class = GetEtsyCategoryAspects


class RemoteGetEtsyCategoryTreeVersion(EtsyAction):
    api_class = GetEtsyCategoryTreeVersion

    def success_trigger(self, message, objects, **kwargs):
        if kwargs.get("save", False):
            EtsyCategoryTree.objects.update_or_create(
                domain=Domain.objects.get(marketplace__unique_name="etsy"),
                defaults={"category_tree_version": objects["results"]["version"]},
            )
        return super().success_trigger(message, objects, **kwargs)


class RemoteGetEtsyCategories(EtsyAction):
    api_class = GetEtsyCategories


class RemoteDownloadEtsyCategories(GetEtsyCategories, DownloadMarketplaceCategories):
    def _get_category_tree(self, **kwargs):
        category_tree, created = EtsyCategoryTree.objects.get_or_create(
            domain=Domain.objects.get(marketplace__unique_name="etsy")
        )
        return category_tree

    def _get_root_node(self, objects):
        return {"children": objects["results"]}

    def _get_categories(self, category_tree, node):
        categories = []
        for child_node in node["children"]:
            parent_id = child_node["parent_id"]
            if not parent_id:
                parent_id = "0"

            is_leaf = not bool(child_node.get("children"))

            if not is_leaf:
                categories += self._get_categories(
                    category_tree=category_tree, node=child_node,
                )

            category = EtsyCategory(
                category_tree=category_tree,
                category_id=str(child_node["id"]),
                old_category_id=child_node["category_id"],
                parent_id=parent_id,
                level=child_node["level"] + 1,
                name=child_node["name"],
                name_path=" / ".join(child_node["path"].split(".")),
                id_path=" / ".join(
                    str(id) for id in child_node["full_path_taxonomy_ids"]
                ),
                is_leaf=is_leaf,
            )
            categories.append(category)

        return categories
