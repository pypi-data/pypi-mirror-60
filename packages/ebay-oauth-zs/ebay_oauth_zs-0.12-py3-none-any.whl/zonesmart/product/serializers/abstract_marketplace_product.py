from rest_framework import serializers

from zonesmart.product.models import AbstractMarketplaceProduct
from zonesmart.product.serializers import ProductImageSerializer


class AbstractMarketplaceProductSerializer(serializers.ModelSerializer):
    FIELDS_FOR_COPY_FROM_BASE_PRODUCT = [
        "title",
        "description",
        "value",
        "currency",
        "main_image",
    ]
    main_image = ProductImageSerializer(read_only=True)
    extra_images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = AbstractMarketplaceProduct
        fields = [
            "id",
            "sku",
            "name",
            "description",
            "quantity",
            "main_image",
            "extra_images",
            "product_id_code_type",
            "product_id_code",
            "value",
            "currency",
            "converted_from_value",
            "converted_from_currency",
            "created",
            "modified",
            "status",
            "published_at",
            "base_product",
            "channel",
        ]
        abstract = True
        extra_kwargs = {
            "sku": {"required": False},
            "title": {"required": False},
            "description": {"required": False},
            "value": {"required": False},
            "currency": {"required": False},
        }

    def create(self, validated_data):
        base_product = validated_data["base_product"]
        # Get field from the base product if it doesn't exists
        for field in self.FIELDS_FOR_COPY_FROM_BASE_PRODUCT:
            if field not in validated_data:
                validated_data[field] = getattr(base_product, field)
        # Save instance before m2m field set
        instance = self.Meta.model.objects.create(**validated_data)
        # Copy extra images from base product
        # instance.extra_images.add(*base_product.extra_images.all())
        # instance.save()
        # Return marketplace product
        return instance
