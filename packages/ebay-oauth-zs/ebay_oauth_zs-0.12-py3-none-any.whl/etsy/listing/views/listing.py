from django.db.models import QuerySet

from etsy.listing.actions.listing_download import RemoteDownloadEtsyListingList
from etsy.listing.serializers.listing.base import BaseEtsyListingSerializer
from etsy.listing.serializers.listing.create import CreateEtsyListingSerializer
from etsy.listing.serializers.listing.update import UpdateEtsyListingSerializer

from zonesmart.views import GenericSerializerModelViewSet
from zonesmart import remote_action_views


class EtsyListingViewSet(
    remote_action_views.RemoteDownloadListActionByChannel, GenericSerializerModelViewSet
):
    remote_api_actions = {"remote_download_list": RemoteDownloadEtsyListingList}
    serializer_classes = {
        "default": BaseEtsyListingSerializer,
        "create": CreateEtsyListingSerializer,
        "update": UpdateEtsyListingSerializer,
        "partial_update": UpdateEtsyListingSerializer,
    }

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(channel__marketplace_user_account__user=self.request.user)
        )
