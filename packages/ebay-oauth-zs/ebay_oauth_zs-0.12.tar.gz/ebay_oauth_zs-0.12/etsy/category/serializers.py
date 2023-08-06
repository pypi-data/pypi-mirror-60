from rest_framework import serializers

from etsy.category.models import EtsyCategory


class EtsyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EtsyCategory
        exclude = [
            "category_tree",
            "old_category_id",
            "id_path",
        ]
