from django.db.models import QuerySet

from etsy.policy.actions import RemoteGetEtsyShippingTemplateList
from etsy.policy.models import EtsyShippingTemplateEntry
from etsy.policy.serializers.shipping.base import (
    BaseEtsyShippingTemplateSerializer,
    BaseEtsyShippingTemplateEntrySerializer,
)
from etsy.policy.serializers.shipping.create import (
    CreateEtsyShippingTemplateSerializer,
    CreateOrUpdateEtsyShippingTemplateEntrySerializer,
)
from etsy.policy.serializers.shipping.update import UpdateEtsyShippingTemplateSerializer
from zonesmart.views import GenericSerializerModelViewSet, GenericSerializerViewSet
from zonesmart import remote_action_views
from rest_framework import mixins, serializers


class ShippingTemplateViewSet(
    remote_action_views.RemoteDownloadListActionByMarketplaceAccount,
    GenericSerializerModelViewSet,
):
    remote_api_actions = {
        "remote_download_list": RemoteGetEtsyShippingTemplateList,
    }
    serializer_classes = {
        "default": BaseEtsyShippingTemplateSerializer,
        "update": UpdateEtsyShippingTemplateSerializer,
        "partial_update": UpdateEtsyShippingTemplateSerializer,
        "create": CreateEtsyShippingTemplateSerializer,
    }

    def get_queryset(self) -> QuerySet:
        qs = (
            super()
            .get_queryset()
            .filter(marketplace_user_account__user=self.request.user)
        )

        if self.action in ["retrieve", "list"]:
            qs.select_related("entries")

        return qs


class ShippingTemplateEntryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericSerializerViewSet,
):
    serializer_classes = {
        "default": BaseEtsyShippingTemplateEntrySerializer,
        "create": CreateOrUpdateEtsyShippingTemplateEntrySerializer,
    }

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(shipping_template=self.kwargs["shipping_template_id"])
        )

    def perform_create(self, serializer):
        serializer.save(shipping_template_id=self.kwargs["shipping_template_id"])

    def perform_destroy(self, instance: EtsyShippingTemplateEntry):
        if instance.shipping_template.entries.count() == 1:
            raise serializers.ValidationError(
                {"detail": "Политика доставки должна содержать хотябы одну страну."}
            )
        instance.delete()
