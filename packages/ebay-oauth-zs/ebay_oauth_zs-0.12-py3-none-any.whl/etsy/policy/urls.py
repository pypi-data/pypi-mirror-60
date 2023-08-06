from rest_framework_nested.routers import SimpleRouter, NestedSimpleRouter

from etsy.policy.views.payment_template import PaymentTemplateViewSet
from etsy.policy.views.shipping_template import (
    ShippingTemplateViewSet,
    ShippingTemplateEntryViewSet,
)

app_name = "etsy.shipping"

router = SimpleRouter()
router.register("shipping", ShippingTemplateViewSet, basename="shipping")
router.register("payment", PaymentTemplateViewSet, basename="payment")

shipping_router = NestedSimpleRouter(router, "shipping", lookup="shipping_template")
shipping_router.register(
    "entries", ShippingTemplateEntryViewSet, basename="shipping-template-entries"
)

urlpatterns = router.urls
urlpatterns += shipping_router.urls
