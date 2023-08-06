from etsy.listing.models import EtsyListing
from rest_framework import serializers


class BaseEtsyListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtsyListing
        exclude = [
            "id",
        ]

    def create(self, validated_data):
        channel = validated_data.pop("channel")
        listing_id = validated_data.pop("listing_id")
        instance, updated = self.Meta.model.objects.update_or_create(
            channel=channel, listing_id=listing_id, defaults=validated_data
        )
        return instance
