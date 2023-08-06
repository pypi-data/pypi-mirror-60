from rest_framework.viewsets import ReadOnlyModelViewSet

from etsy.order.serializers.receipt import BaseEtsyReceiptSerializer


class EtsyReceiptViewSet(ReadOnlyModelViewSet):
    serializer_class = BaseEtsyReceiptSerializer

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(
            marketplace_user_account__user=self.request.user
        )
