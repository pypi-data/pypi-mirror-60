from django_filters import rest_framework as filters
from ebay.category.models import EbayCategory


class EbayCategoryFilter(filters.FilterSet):
    domain_id = filters.NumberFilter(
        field_name="category_tree", lookup_expr="domain_id"
    )
    variations_supported = filters.BooleanFilter(field_name="variationsSupported")
    transport_supported = filters.BooleanFilter(field_name="transportSupported")

    class Meta:
        model = EbayCategory
        fields = [
            "parent_id",
            "level",
            "domain_id",
            "is_leaf",
            "category_id",
            "variations_supported",
            "transport_supported",
        ]
