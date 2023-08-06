from rest_framework.viewsets import ReadOnlyModelViewSet

from etsy.category.filters import EtsyCategoryFilterSet
from etsy.category.serializers import EtsyCategorySerializer


class EtsyCategoryViewSet(ReadOnlyModelViewSet):
    serializer_class = EtsyCategorySerializer
    queryset = EtsyCategorySerializer.Meta.model.objects.all()
    filterset_class = EtsyCategoryFilterSet
