from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from etsy.serializers.base import BaseEtsyCountrySerializer, BaseEtsyRegionSerializer


class EtsyCountryViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet,
):
    serializer_class = BaseEtsyCountrySerializer
    queryset = BaseEtsyCountrySerializer.Meta.model.objects.all()
    lookup_field = "country_id"


class EtsyRegionViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet,
):
    serializer_class = BaseEtsyRegionSerializer
    queryset = BaseEtsyRegionSerializer.Meta.model.objects.all()
    lookup_field = "region_id"
