from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from zonesmart.marketplace import views

app_name = "zonesmart.marketplace"

router = DefaultRouter()

router.register(r"channel", views.ChannelViewSet, basename="channel")
router.register(
    r"user_account", views.MarketplaceUserAccountViewSet, basename="user_account"
)

router.register(r"", views.MarketplaceReadOnlyViewSet, basename="marketplace")
domain_router = NestedDefaultRouter(router, r"", lookup="marketplace")
domain_router.register(
    r"domain", views.DomainReadOnlyViewSet, basename="marketplace-domain"
)

urlpatterns = router.urls
urlpatterns += domain_router.urls  # в одну строку?
