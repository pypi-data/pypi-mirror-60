from ebay.policy.serializers.fulfillment_policy import BaseFulfillmentPolicySerializer


class UpdateFulfillmentPolicySerializer(BaseFulfillmentPolicySerializer):
    class Meta(BaseFulfillmentPolicySerializer.Meta):
        read_only_fields = BaseFulfillmentPolicySerializer.Meta.read_only_fields + [
            "channel",
            "policy_id",
        ]
