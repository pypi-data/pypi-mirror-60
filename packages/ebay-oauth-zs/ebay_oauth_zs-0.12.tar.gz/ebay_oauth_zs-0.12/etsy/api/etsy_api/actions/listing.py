from ..base_api import EtsyAPI


class GetEtsyShopActiveListings(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_findallshoplistingsactive
    """

    api_method_name = "findAllShopListingsActive"
    params = ["shop_id"]


class GetEtsyShopInactiveListings(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_findallshoplistingsinactive
    """

    api_method_name = "findAllShopListingsInactive"
    params = ["shop_id"]


class GetEtsyShopDraftListings(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_findallshoplistingsdraft
    """

    api_method_name = "findAllShopListingsDraft"
    params = ["shop_id"]


class GetEtsyShopExpiredListings(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_findallshoplistingsexpired
    """

    api_method_name = "findAllShopListingsExpired"
    params = ["shop_id"]


class GetEtsySingleListing(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_getlisting
    """

    api_method_name = "getListing"
    params = ["listing_id"]


class GetEtsyListingProductList(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listinginventory#method_getinventory
    """

    api_method_name = "getInventory"
    params = ["listing_id"]


class GetEtsyProduct(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listingproduct#method_getproduct
    """

    api_method_name = "getProduct"
    params = ["listing_id", "product_id"]


class GetEtsyOffering(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listingoffering#method_getoffering
    """

    api_method_name = "getOffering"
    params = ["listing_id", "product_id", "offering_id"]


class GetEtsyListingAttibuteList(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/propertyvalue#method_getattributes
    """

    api_method_name = "getAttributes"
    params = ["listing_id"]


class GetEtsyListingAttibute(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/propertyvalue#method_getattribute
    """

    api_method_name = "getAttribute"
    params = ["listing_id", "property_id"]


class CreateOrUpdateEtsyListingAttibute(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/propertyvalue#method_updateattribute
    """

    api_method_name = "updateAttribute"
    params = [
        "listing_id",
        "property_id",
        # body
        "value_ids",
        "values",
        "scale_id",
    ]


class DeleteEtsyListingAttibute(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/propertyvalue#method_deleteattribute
    """

    api_method_name = "deleteAttribute"
    params = ["listing_id", "property_id"]


class DeleteEtsyListing(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_deletelisting
    """

    api_method_name = "deleteListing"
    params = ["listing_id"]


class GetEtsyReceiptListings(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_findallreceiptlistings
    """

    api_method_name = "findAllReceiptListings"
    params = ["receipt_id"]


class GetEtsyShopSectionListings(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_findallshopsectionlistings
    """

    api_method_name = "findAllShopSectionListings"
    params = ["shop_id", "shop_section_id"]


class CreateEtsySingleListing(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_createlisting
    """

    api_method_name = "createListing"
    params = [
        # body
        # required
        "quantity",
        "title",
        "description",
        "price",
        "who_made",
        "is_supply",
        "when_made",
        # optional
        "materials",
        "shipping_template_id",
        "shop_section_id",
        "image_ids",
        "image",
        "state",
        "taxonomy_id",
    ]


class UpdateEtsySingleListing(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#method_updatelisting
    """

    api_method_name = "updateListing"
    params = [
        "listing_id",
        # body
        "title",
        "description",
        "materials",
        "renew",
        "shipping_template_id",
        "shop_section_id",
        "image_ids",
        "state",
        "taxonomy_id",
        "who_made",
        "is_supply",
        "when_made",
    ]


class UpdateEtsyListingInventory(EtsyAPI):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listinginventory#method_updateinventory
    """

    api_method_name = "updateInventory"
    params = [
        "listing_id",
        # body
        "products",
        "price_on_property",
        "quantity_on_property",
        "sku_on_property",
    ]


class GetSuggestedStyles(EtsyAPI):
    api_method_name = "findSuggestedStyles"
