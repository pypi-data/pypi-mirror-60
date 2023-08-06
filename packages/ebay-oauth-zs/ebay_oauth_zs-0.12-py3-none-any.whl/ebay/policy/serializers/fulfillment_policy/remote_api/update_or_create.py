from ebay.policy.serializers.fulfillment_policy import BaseFulfillmentPolicySerializer
from rest_framework import serializers

from zonesmart.serializers import NotNullAndEmptyStringModelSerializer


class UpdateOrCreateFulfillmentPolicySerializer(
    BaseFulfillmentPolicySerializer, NotNullAndEmptyStringModelSerializer
):
    marketplaceId = serializers.CharField(source="channel.domain.code")

    class Meta:
        model = BaseFulfillmentPolicySerializer.Meta.model
        exclude = [
            "id",
            "channel",
            "status",
            "created",
            "modified",
            "published_at",
        ]
