from ebay.category.models import EbayCategory
from rest_framework import serializers


class EbayCategorySerializer(serializers.ModelSerializer):
    domain_id = serializers.IntegerField(source="category_tree.domain.id")

    class Meta:
        model = EbayCategory
        fields = [
            "id",
            "domain_id",
            "category_id",
            "parent_id",
            "level",
            "name",
            "name_path",
            "is_leaf",
            "variationsSupported",
            "transportSupported",
        ]
