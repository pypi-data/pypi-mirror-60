from django.urls import include, path
from rest_framework.routers import DefaultRouter

from etsy.category.views import EtsyCategoryViewSet
from etsy.order.views import EtsyReceiptViewSet
from etsy.views import EtsyCountryViewSet, EtsyRegionViewSet

app_name = "etsy"


router = DefaultRouter()
router.register("country", EtsyCountryViewSet, basename="country")
router.register("region", EtsyRegionViewSet, basename="region")
router.register("category", EtsyCategoryViewSet, basename="category")
router.register("order", EtsyReceiptViewSet, basename="order")


urlpatterns = [
    path("account/", include("etsy.account.urls", namespace="account")),
    path("listing/", include("etsy.listing.urls", namespace="listing")),
    path("policy/", include("etsy.policy.urls", namespace="policy")),
]

urlpatterns += router.urls
