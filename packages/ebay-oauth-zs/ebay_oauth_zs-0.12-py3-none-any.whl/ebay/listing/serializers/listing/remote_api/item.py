from ebay.listing.models import EbayProduct
from rest_framework import serializers

from zonesmart.product.models import ProductImage
from zonesmart.serializers import ModelSerializerWithoutNullAndEmptyObjects


class ProductSerializer(serializers.ModelSerializer):
    aspects = serializers.SerializerMethodField()

    class Meta:
        model = EbayProduct
        fields = ["aspects", "description", "epid"]

    @staticmethod
    def get_aspects(instance: EbayProduct):
        aspects = dict()
        if instance.specifications.exists():
            for aspect in instance.specifications.all().values_list("name", "value"):
                name, value = aspect
                aspects[name] = [value]
        return aspects

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Image urls represent
        qs = instance.extra_images.all().union(
            ProductImage.objects.filter(id=instance.main_image.id)
        )
        representation["imageUrls"] = [image.get_url() for image in qs]
        # Return representation
        return representation


class ItemSerializer(ModelSerializerWithoutNullAndEmptyObjects):
    product = ProductSerializer(source="*")

    def __init__(self, **kwargs):
        self.listing_aspects_representation = kwargs.pop(
            "listing_aspects_representation", None
        )
        self.title = kwargs.pop("title")
        self.locale = kwargs.pop("locale")
        super().__init__(**kwargs)

    class Meta:
        model = EbayProduct
        fields = ["condition", "conditionDescription", "product", "sku"]

    def to_representation(self, instance: EbayProduct):
        representation = super().to_representation(instance)
        product_representation = representation["product"]
        # Add listing aspects if exists
        if self.listing_aspects_representation:
            product_representation["aspects"].update(
                self.listing_aspects_representation
            )
        # Add product title
        product_representation["title"] = self.title
        representation["locale"] = self.locale
        # Add availability representation
        representation["availability"] = {
            "shipToLocationAvailability": {"quantity": instance.quantity}
        }
        # Return representation
        return self.clean_representation(representation)
