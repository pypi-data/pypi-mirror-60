from ebay.policy.serializers.fulfillment_policy import BaseFulfillmentPolicySerializer


class RemoteDownloadFulfillmentPolicySerializer(BaseFulfillmentPolicySerializer):
    class Meta(BaseFulfillmentPolicySerializer.Meta):
        read_only_fields = ["id"]
