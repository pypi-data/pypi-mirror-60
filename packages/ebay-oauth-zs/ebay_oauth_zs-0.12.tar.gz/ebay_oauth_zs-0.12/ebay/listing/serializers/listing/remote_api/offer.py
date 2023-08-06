from ebay.listing.models import EbayProduct
from rest_framework import serializers

from zonesmart.serializers import ModelSerializerWithoutNullAndEmptyObjects


class OfferSerializer(ModelSerializerWithoutNullAndEmptyObjects):
    format = serializers.CharField(source="format_type")

    def __init__(self, *args, **kwargs):
        self.marketplace_id = kwargs.pop("marketplace_id")
        self.category_id = kwargs.pop("category_id")
        self.listing_polices_representation = kwargs.pop(
            "listing_polices_representation"
        )
        self.listing_description = kwargs.pop("listing_description")
        self.merchant_location_key = kwargs.pop("merchant_location_key")
        super().__init__(*args, **kwargs)

    class Meta:
        model = EbayProduct
        fields = ["sku", "format", "quantityLimitPerBuyer"]

    def to_representation(self, instance: EbayProduct):
        representation = super().to_representation(instance)
        representation["marketplaceId"] = self.marketplace_id
        representation["categoryId"] = self.category_id
        representation["pricingSummary"] = {
            "price": {"value": instance.value, "currency": instance.currency}
        }
        representation["listingPolicies"] = self.listing_polices_representation
        representation["listingDescription"] = self.listing_description
        representation["merchantLocationKey"] = self.merchant_location_key
        return representation
