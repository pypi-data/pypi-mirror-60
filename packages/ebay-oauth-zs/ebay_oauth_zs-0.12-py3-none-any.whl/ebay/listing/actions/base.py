from ebay.api.ebay_action import EbayEntityAction
from ebay.listing.models import EbayListing

from zonesmart.utils.logger import get_logger

logger = get_logger("ebay_listing_actions")


class EbayListingAction(EbayEntityAction):
    description = "Действие с листингом eBay"
    entity_name = "listing"
    entity_model = EbayListing
