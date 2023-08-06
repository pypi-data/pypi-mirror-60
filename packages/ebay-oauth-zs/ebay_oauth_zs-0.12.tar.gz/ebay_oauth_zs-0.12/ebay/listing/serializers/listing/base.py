import copy

from ebay.listing.models import EbayListing, EbayListingAspect
from ebay.listing.serializers.helpers import aspects_to_representation
from ebay.listing.serializers.listing.compatibility.base import (
    BaseEbayProductCompatibilitySerializer,
)
from ebay.listing.serializers.product.base import BaseEbayProductSerializer
from ebay.listing.serializers.validators import EbayListingValidator
from rest_framework import serializers

from zonesmart.product.serializers import AbstractMarketplaceProductSerializer


class BaseEbayListingAspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = EbayListingAspect
        exclude = ["id", "listing"]


class BaseEbayListingSerializer(AbstractMarketplaceProductSerializer):
    FIELDS_FOR_COPY_FROM_BASE_PRODUCT = [
        "title",
    ]

    aspects = BaseEbayListingAspectSerializer(
        required=False, many=True, allow_null=False
    )
    products = BaseEbayProductSerializer(many=True)
    compatibilities = BaseEbayProductCompatibilitySerializer(
        required=False, many=True, allow_null=False
    )

    class Meta:
        model = EbayListing
        fields = [
            "id",
            "channel",
            "base_product",
            "status",
            "title",
            "listing_sku",
            "listing_description",
            "groupListingId",
            "location",
            "category",
            "fulfillmentPolicy",
            "paymentPolicy",
            "returnPolicy",
            "aspects",
            "products",
            "compatibilities",
        ]
        extra_kwargs = {
            "title": {"required": False,},
            "location": {"required": True},
            "fulfillmentPolicy": {"required": True},
            "paymentPolicy": {"required": True},
            "returnPolicy": {"required": True},
        }

    def to_internal_value(self, data):
        # Parse aspects into the applicable data
        if "aspects" in data:
            aspects = list()
            for name, values in data["aspects"].items():
                for value in values:
                    aspects.append({"name": name, "value": value})
            data["aspects"] = aspects
        return super().to_internal_value(data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if "aspects" in representation:
            representation["aspects"] = aspects_to_representation(
                representation["aspects"]
            )
        return representation

    def validate(self, data: dict):
        self.instance: EbayListing
        kwargs = dict()
        # Create copy of data to validate
        data_copy = copy.deepcopy(data)
        # Get needed data by keys from copy
        for key in ["aspects", "products", "category", "channel", "compatibilities"]:
            if key in data_copy:
                kwargs.update({key: data_copy[key]})
        # If instance is exists add additional kwargs
        if self.instance:
            kwargs["instance"] = self.instance
            for key in ["category", "channel"]:
                if key not in kwargs:
                    kwargs[key] = getattr(self.instance, key)
        # Initialize validator with created kwargs
        validator = EbayListingValidator(**kwargs)
        # Call validate method and get errors list
        errors = validator.validate()
        # If errors list exists -> raise ValidatorError with errors list of dicts
        if errors:
            raise serializers.ValidationError(*errors)
        # Otherwise return validated data
        return data

    def update(self, instance: EbayListing, validated_data):
        # Update listing
        instance, created = EbayListing.objects.update_or_create(
            channel=instance.channel,
            listing_sku=instance.listing_sku,
            defaults=validated_data,
        )
        return instance
