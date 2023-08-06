from rest_framework import serializers

from etsy.listing.serializers.listing.base import (
    BaseEtsyProductSerializer,
    BaseEtsyListingSerializer,
)


class CreateEtsyProductSerializer(BaseEtsyProductSerializer):
    class Meta:
        model = BaseEtsyProductSerializer.Meta.model
        fields = [
            "sku",
            "price",
            "quantity",
            "is_enabled",
        ]


class CreateEtsyListingSerializer(BaseEtsyListingSerializer):
    products = CreateEtsyProductSerializer(
        many=True, allow_null=False, allow_empty=False
    )
    style = serializers.ListField(required=False)

    class Meta(BaseEtsyListingSerializer.Meta):
        fields = [
            "channel",
            "base_product",
            # Fields
            # "quantity"  # total_quantity auto calc on save
            "title",
            "description",
            "price",
            # "materials",
            "shipping_template",
            "shop_section",
            # image_ids: product main image + extra images
            "is_customizable",
            # "non_taxable",
            # "image",
            "state",
            # "processing_min",
            # "processing_max",
            "category",  # also contains taxonomy_id
            # "tags",
            "who_made",
            "is_supply",
            "when_made",
            # "recipient",
            # "occasion",
            "style",
            "products",
        ]

    def create(self, validated_data):
        return self.Meta.model.objects.create(**validated_data)
