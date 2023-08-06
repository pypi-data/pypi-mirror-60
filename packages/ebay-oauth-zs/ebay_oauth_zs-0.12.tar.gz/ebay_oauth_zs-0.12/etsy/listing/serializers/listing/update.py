from etsy.listing.serializers.listing.base import (
    BaseEtsyProductSerializer,
    BaseEtsyListingSerializer,
)


class UpdateEtsyProductSerializer(BaseEtsyProductSerializer):
    class Meta:
        model = BaseEtsyProductSerializer.Meta.model
        fields = "__all__"  # TODO: add filed list for update


class UpdateEtsyListingSerializer(BaseEtsyListingSerializer):
    products = UpdateEtsyProductSerializer(required=False, many=True)

    class Meta(BaseEtsyListingSerializer.Meta):
        fields = [
            "title",
            "description",
            # "materials",
            # "renew",
            "shipping_template",
            "shop_section",
            "state",
            # image_ids: product main image + extra images
            "is_customizable",
            # "item_weight",
            # "item_length",
            # "item_width",
            # "item_height",
            # "item_weight_unit",
            # "item_dimensions_unit",
            # "non_taxable",
            "category",  # category contains taxonomy_id
            # "tags",
            "who_made",
            "is_supply",
            "when_made",
            # "recipient",
            # "occasion",
            "style",
            # "processing_min",
            # "processing_max",
            # "featured_rank",
            "products",
        ]
        extra_kwargs = {
            "title": {"required": False},
            "description": {"required": False},
            "category": {"required": False},
        }
