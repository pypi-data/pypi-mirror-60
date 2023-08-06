from abc import abstractmethod

from amazon.api.amazon_access import AmazonAPIAccess
from amazon.api.core.feeds import Feeds
from amazon.api.core.orders import Orders
from amazon.api.core.reports import Reports
from amazon.api.core.sellers import Sellers

from zonesmart.marketplace.api.marketplace_action import MarketplaceAction


class AmazonActionError(Exception):
    response = None


class AmazonAction(AmazonAPIAccess, MarketplaceAction):
    description = "Действие Amazon"
    exception_class = AmazonActionError

    @property
    @abstractmethod
    def api_class(self):
        pass

    @property
    def api(self):
        if not getattr(self, "_api", None):
            self._api = self.api_class(
                auth_token=self.account.access_token, **self.credentials,
            )
        return self._api


class AmazonOrderAction(AmazonAction):
    description = "Действие с заказами Amazon"
    api_class = Orders


class AmazonFeedAction(AmazonAction):
    description = "Действие с фидами Amazon"
    api_class = Feeds


class AmazonSellerAction(AmazonAction):
    description = "Действие с данными о пользователе Amazon"
    api_class = Sellers


class AmazonReportAction(AmazonAction):
    description = "Действие с отчётами Amazon"
    api_class = Reports
