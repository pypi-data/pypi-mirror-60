import datetime

from ebay.api.ebay_action import EbayAccountAction
from ebay.api.ebay_trading_api_action import EbayTradingAPIAction

from zonesmart.utils.logger import get_logger

logger = get_logger("ebay_listings")


class GetEbayOldStyleListingIds(EbayTradingAPIAction):
    # https://developer.ebay.com/devzone/xml/docs/reference/ebay/GetSellerList.html
    verb = "GetSellerList"
    success_message = "Список активных листингов успешно получен."
    failure_message = "Не удалось получить список активных листингов."

    def get_params(self, EndTimeFrom=None, EndTimeTo=None, **kwargs):
        if isinstance(EndTimeTo, str):
            EndTimeTo = datetime.datetime.fromisoformat(EndTimeTo)
        if isinstance(EndTimeFrom, str):
            EndTimeFrom = datetime.datetime.fromisoformat(EndTimeFrom)
        if not EndTimeFrom:
            EndTimeFrom = datetime.datetime.now()
        if (not EndTimeTo) or ((EndTimeTo - EndTimeFrom).days > 120):
            EndTimeTo = EndTimeFrom + datetime.timedelta(days=120)

        logger.debug(f"EndTimeFrom: {EndTimeFrom}\n" f"EndTimeTo: {EndTimeTo}")

        params = {
            "EndTimeFrom": EndTimeFrom.isoformat(),
            "EndTimeTo": EndTimeTo.isoformat(),
            "WarningLevel": "High",
            "Pagination": {
                "EntriesPerPage": kwargs.get("entries_per_page", 100),
                "PageNumber": kwargs.get("page_number", 1),
            },
        }

        return params

    def make_request(self, ids_only: bool = True, **kwargs):
        listing_ids = []
        while True:
            is_success, message, objects = super().make_request(**kwargs)
            if not is_success:
                return is_success, message, objects

            listing_ids += objects["results"]["ItemArray"]["Item"]

            page_number = int(objects["results"].get("PageNumber", 1))
            number_of_pages = int(
                objects["results"]["PaginationResult"].get("TotalNumberOfPages", 1)
            )

            if page_number < number_of_pages:
                kwargs["page_number"] = str(page_number + 1)
            else:
                break

        if ids_only:
            listing_ids = [item["ItemID"] for item in listing_ids]

        objects = {"results": listing_ids}
        return is_success, message, objects


class GetEbayOldStyleListing(EbayTradingAPIAction):
    # https://developer.ebay.com/devzone/xml/docs/Reference/eBay/GetItem.html
    verb = "GetItem"

    def get_params(self, listingId: str, detail_level="ReturnAll", **kwargs):
        return {
            "ItemID": listingId,
            "IncludeItemCompatibilityList": True,
            "IncludeItemSpecifics": True,
            "DetailLevel": detail_level,
        }

    def success_trigger(self, message: str, objects: dict, **kwargs):
        objects["results"] = objects["results"]["Item"]
        return super().success_trigger(message, objects, **kwargs)


class GetEbayOldStyleListingList(EbayAccountAction):
    api_class = None

    def make_request(self, **kwargs):
        is_success, message, objects = GetEbayOldStyleListingIds(instance=self)(
            ids_only=True
        )

        if is_success:
            get_listing = GetEbayOldStyleListing(instance=self)
            results = []
            for listingId in objects["results"]:
                is_success, message, objects = get_listing(listingId=listingId)

                if not is_success:
                    break

                item = objects["results"]
                results.append(
                    {
                        "listingId": item["ItemID"],
                        "listing_sku": item.get("SKU", ""),
                        "variations_sku": [
                            variation["SKU"]
                            for variation in item.get("Variations", {}).get(
                                "Variation", {}
                            )
                            if variation.get("SKU", "")
                        ],
                    }
                )
            else:
                is_success = True
                message = "SKU всех листингов и их вариаций успешно получены"
                objects = {"results": results}

        return is_success, message, objects
