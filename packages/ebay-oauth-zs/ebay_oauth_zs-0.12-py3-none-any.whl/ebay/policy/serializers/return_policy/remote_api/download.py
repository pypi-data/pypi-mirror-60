from ebay.policy.serializers.return_policy import BaseReturnPolicySerializer


class RemoteDownloadReturnPolicySerializer(BaseReturnPolicySerializer):
    class Meta(BaseReturnPolicySerializer.Meta):
        read_only_fields = ["id"]
