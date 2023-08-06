from zonesmart.marketplace.serializers.channel.base import BaseChannelSerializer


class UpdateChannelSerializer(BaseChannelSerializer):
    class Meta(BaseChannelSerializer.Meta):
        read_only_fields = ["id", "domain", "marketplace_user_account"]
