from ebay.order.views import EbayOrderViewSet, EbayShippingFulfillmentViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

app_name = "order"

router = DefaultRouter()
router.register(r"", EbayOrderViewSet, basename="order")

shipping_fulfillment_router = NestedDefaultRouter(router, r"", lookup="order")
shipping_fulfillment_router.register(
    r"shipping_fulfillment",
    EbayShippingFulfillmentViewSet,
    basename="shipping_fulfillment",
)


urlpatterns = router.urls
urlpatterns += shipping_fulfillment_router.urls
