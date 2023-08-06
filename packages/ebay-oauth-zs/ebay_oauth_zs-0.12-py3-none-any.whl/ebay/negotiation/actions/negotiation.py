from ebay.api.ebay_action import EbayChannelAction
from ebay.listing.models import EbayListing
from ebay.negotiation.actions.helpers import deactivate_eligible_items
from ebay.negotiation.models import EbayEligibleItem
from ebay_api.sell.negotiation import FindEligibleItems, SendOfferToInterestedBuyers


class GetEligibleEbayListings(EbayChannelAction):
    # https://developer.ebay.com/api-docs/sell/negotiation/resources/offer/methods/findEligibleItems
    description = "Получение желаемых товаров"
    api_class = FindEligibleItems
    next_token_action = True

    def get_query_params(self, **kwargs):
        if not kwargs.get("limit", None):
            kwargs["limit"] = 1
        return super().get_query_params(**kwargs)


class UpdateEligibleEbayListings(GetEligibleEbayListings):
    def success_trigger(self, message, objects, **kwargs):
        eligible_listing_ids = objects["results"]["eligibleItems"]
        eligible_local_listings = [
            listing
            for listing in EbayListing.objects.all()
            if listing.listingId in eligible_listing_ids
        ]

        # обновление списка желаемых товаров
        deactivate_eligible_items()
        for ebay_listing in eligible_local_listings:
            EbayEligibleItem.objects.update_or_create(
                ebay_listing=ebay_listing, defaults={"active": True},
            )

        return super().success_trigger(message, objects, **kwargs)


class SendEbayBuyerOffers(EbayChannelAction):
    # https://developer.ebay.com/api-docs/sell/negotiation/resources/offer/methods/sendOfferToInterestedBuyers
    description = "Отправление предложения заинтересованным пользователям"
    api_class = SendOfferToInterestedBuyers
    payload_serializer = None
