from zonesmart.marketplace.serializers.channel import (
    BaseChannelSerializer,
    CreateChannelSerializer,
    UpdateChannelSerializer,
)
from zonesmart.views import GenericSerializerModelViewSet


class ChannelViewSet(GenericSerializerModelViewSet):
    """
    ViewSet for Channel model
    """

    serializer_classes = {
        "default": BaseChannelSerializer,
        "create": CreateChannelSerializer,
        "update": UpdateChannelSerializer,
        "partial_update": UpdateChannelSerializer,
    }

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(marketplace_user_account__user=self.request.user)
        )
