from rest_framework.exceptions import ValidationError

from ebay.api.ebay_action import EbayAction, EbayAccountAction
from ebay.account.models import EbayUserAccount, EbayAppAccount
from ebay.account.serializers.ebay_account_info import (
    EbayAppAccountRateLimitsSerializer,
)
from ebay.account.serializers.profile.base import EbayUserAccountProfileSerializer
from ebay.api.ebay_trading_api_action import EbayTradingAPIAction
from ebay_api.commerce.identity import GetUser
from ebay_api.developer import GetAppRateLimits, GetUserRateLimits
from ebay_api.sell.account import GetPrivileges

from zonesmart.utils.logger import get_logger

logger = get_logger(__name__)


def get_ebay_user_account_info(access_token, is_sandbox=False):
    api = GetUser(access_token=access_token, sandbox=is_sandbox,)
    return api.make_request()


class GetEbayUserAccountInfo(EbayAccountAction):
    api_class = GetUser


class RemoteDownloadEbayUserAccountInfo(GetEbayUserAccountInfo):
    def success_trigger(self, message, objects, **kwargs):
        ebay_account = EbayUserAccount.objects.get(
            marketplace_user_account=self.marketplace_user_account,
        )

        api = GetUser(access_token=ebay_account.access_token, sandbox=self.is_sandbox)
        is_success, message, objects = api.make_request()
        if is_success:
            profile_serializer = EbayUserAccountProfileSerializer(
                data=objects["results"]
            )
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save(ebay_user_account=ebay_account)
        else:
            raise ValidationError(
                {
                    "detail": "Не удалось получить информацию о пользователе в системе eBay."
                }
            )
        return super().success_trigger(message, objects, **kwargs)


class GetEbayUserAccountPrivileges(EbayAccountAction):
    api_class = GetPrivileges


class RemoteDownloadEbayUserAccountPrivileges(GetEbayUserAccountPrivileges):
    def success_trigger(self, message, objects, **kwargs):
        # data = objects['results']
        # ebay_account = EbayUserAccount.objects.get(
        #     marketplace_user_account=self.marketplace_user_account,
        # )
        # serializer = EbayUserAccountPrivilegesSerializer(data=data)
        #
        # if serializer.is_valid():
        #     serializer.save(ebay_account=ebay_account)
        # else:
        #     message = str(serializer.errors)
        #     objects['errors'] = serializer.errors
        #     return super().failure_trigger(message, objects, **kwargs)

        return super().success_trigger(message, objects, **kwargs)


# Rate limits
# --------------------------------------------


class GetEbayAppRateLimits(EbayAction):
    description = "Получение лимитов на запросы приложения к API eBay"
    api_class = GetAppRateLimits


class GetEbayUserRateLimits(EbayAccountAction):
    description = "Получение лимитов на запросы пользователя к API eBay"
    api_class = GetUserRateLimits


class RemoteDownloadEbayAppRateLimits(GetEbayAppRateLimits):
    def success_trigger(self, message: str, objects: dict, **kwargs):
        app_account = EbayAppAccount.objects.get_or_create(sandbox=self.is_sandbox)[0]

        for rate_limits_data in objects["results"]["rateLimits"]:
            rate_limits_data.update({"ebay_app_account": app_account.id})
            serializer = EbayAppAccountRateLimitsSerializer(data=rate_limits_data)

            if serializer.is_valid():
                serializer.save()
            else:
                message = str(serializer.errors)
                objects["errors"] = serializer.errors
                return super().failure_trigger(message, objects, **kwargs)

        return super().success_trigger(message=message, objects=objects)


# Selling info
# --------------------------------------------


class GetEbaySellingInfo(EbayTradingAPIAction):
    """
    Docs:
    https://developer.ebay.com/devzone/xml/docs/reference/ebay/GetMyeBaySelling.html
    """

    verb = "GetMyeBaySelling"

    containers = [
        "ActiveList",
        "DeletedFromSoldList",
        "DeletedFromUnsoldList",
        "ScheduledList",
        "SoldList",
        "UnsoldList",
        "SellingSummary",
    ]

    def get_params(self, **kwargs):
        return {
            container: {"Include": kwargs.get(container, False)}
            for container in self.containers
        }


class GetEbaySellingSummary(GetEbaySellingInfo):
    def get_params(self, **kwargs):
        kwargs.update({container: False for container in self.containers})
        kwargs["SellingSummary"] = True
        return super().get_params(**kwargs)

    def success_trigger(self, message, objects, **kwargs):
        summary = objects["results"]["Summary"]
        objects["results"] = {
            "quantity_limit": summary["QuantityLimitRemaining"],
            "amount_limit_value": summary["AmountLimitRemaining"]["value"],
            "amount_limit_currency": summary["AmountLimitRemaining"]["_currencyID"],
            "total_sold_value": summary["TotalSoldValue"]["value"],
            "total_sold_currency": summary["TotalSoldValue"]["_currencyID"],
        }
        return super().success_trigger(message, objects, **kwargs)
