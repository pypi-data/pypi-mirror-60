from ebay.negotiation.models import EbayMessage
from rest_framework import serializers


class BaseEbayMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EbayMessage
        exclude = []


class DownloadEbayMessageSerializer(BaseEbayMessageSerializer):
    class Meta(BaseEbayMessageSerializer.Meta):
        exclude = BaseEbayMessageSerializer.Meta.exclude + [
            "marketplace_user_account",
            "listing",
        ]
        extra_kwargs = {"message_id": {"validators": []}}

    def create(self, validated_data):
        message_id = validated_data.pop("message_id")
        instance, created = self.Meta.model.objects.update_or_create(
            message_id=message_id, defaults=validated_data
        )
        return instance
