from etsy.account.models import EtsyShopSection
from etsy.api.etsy_action import EtsyAccountAction
from etsy.api.etsy_api.actions.listing import (
    GetEtsyShopExpiredListings,
    GetEtsyShopDraftListings,
    GetEtsyShopInactiveListings,
    GetEtsyShopActiveListings,
    GetEtsyListingAttibuteList,
    GetEtsyListingProductList,
    GetEtsySingleListing,
)

from etsy.category.models import EtsyCategory
from etsy.listing.serializers.listing.remote.download import (
    DownloadEtsyListingSerializer,
)
from zonesmart.product.models import BaseProduct


class RemoteGetEtsyShopExpiredListings(EtsyAccountAction):
    api_class = GetEtsyShopExpiredListings


class RemoteGetEtsyShopDraftListings(EtsyAccountAction):
    api_class = GetEtsyShopDraftListings


class RemoteGetEtsyShopInactiveListings(EtsyAccountAction):
    api_class = GetEtsyShopInactiveListings


class RemoteGetEtsyShopActiveListings(EtsyAccountAction):
    api_class = GetEtsyShopActiveListings


class RemoteGetEtsySingleListingList(EtsyAccountAction):
    def get_expired_listings(self):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEtsyShopExpiredListings,
        )
        return objects["results"]

    def get_draft_listings(self):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEtsyShopDraftListings,
        )
        return objects["results"]

    def get_inactive_listings(self):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEtsyShopInactiveListings,
        )
        return objects["results"]

    def get_active_listings(self):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEtsyShopActiveListings,
        )
        return objects["results"]

    def make_request(self, **kwargs):
        try:
            results = [
                *self.get_expired_listings(),
                *self.get_draft_listings(),
                *self.get_inactive_listings(),
                *self.get_active_listings(),
            ]
        except self.exception_class as error:
            is_success = False
            errors = str(error)
            message = f"Не удалось получить листинги Etsy.\n{errors}"
            objects = {"errors": errors}
        else:
            is_success = True
            message = "Все листинги Etsy успешно получены."
            objects = {
                "count": len(results),
                "results": results,
            }
        return is_success, message, objects


class RemoteGetEtsyListingAttibuteList(EtsyAccountAction):
    api_class = GetEtsyListingAttibuteList


class RemoteGetEtsyListingProductList(EtsyAccountAction):
    api_class = GetEtsyListingProductList


class RemoteGetEtsyListingList(RemoteGetEtsySingleListingList):
    def get_listing_attributes(self, listing_id: int):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEtsyListingAttibuteList, listing_id=listing_id,
        )
        return {"attributes": objects["results"]}

    def get_listing_products(self, listing_id: int):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEtsyListingProductList, listing_id=listing_id,
        )
        return objects["results"]

    def success_trigger(self, message, objects, **kwargs):
        updated_results = []
        for listing_data in objects["results"]:
            products_data = self.get_listing_products(
                listing_id=listing_data["listing_id"]
            )
            attributes_data = self.get_listing_attributes(
                listing_id=listing_data["listing_id"]
            )
            updated_results.append({**listing_data, **products_data, **attributes_data})
        objects["results"] = updated_results
        return super().success_trigger(message, objects, **kwargs)


class RemoteDownloadEtsyListingList(RemoteGetEtsyListingList):
    def get_base_product(self, listings: list) -> BaseProduct:
        listing: dict = listings[0]
        product = listing["products"][0]
        defaults = {
            "value": listing["price"],
            "currency": listing["currency_code"],
            "title": listing["title"],
            "description": listing["description"],
            "quantity": listing["quantity"],
        }
        # Create BaseProduct
        base_product, created = BaseProduct.objects.update_or_create(
            user=self.marketplace_user_account.user,
            sku=product["sku"],
            defaults=defaults,
        )
        return base_product

    def success_trigger(self, message, objects, **kwargs):
        is_success, message, objects = super().success_trigger(
            message, objects, **kwargs
        )
        base_product = self.get_base_product(objects["results"])
        for listing in objects["results"]:
            category = EtsyCategory.objects.get(category_id=listing.pop("taxonomy_id"))
            shop_section = EtsyShopSection.objects.get(
                shop_section_id=listing.pop("shop_section_id")
            )
            # Add additional fields from offering for each product
            for p in listing["products"]:
                offering = p.pop("offerings")[0]
                p["price"] = offering["price"]["amount"]
                for k in ["offering_id", "quantity", "is_enabled"]:
                    p[k] = offering[k]
                # If product sku is a blank -> pass id to it
                if not p["sku"]:
                    p["sku"] = p["product_id"]
            # Validate & save listing
            serializer = DownloadEtsyListingSerializer(data=listing)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                base_product=base_product,
                channel=self.channel,
                category=category,
                shop_section=shop_section,
            )
        return is_success, message, objects


class RemoteGetEtsySingleListing(EtsyAccountAction):
    api_class = GetEtsySingleListing


class RemoteGetEtsyListing(EtsyAccountAction):
    def get_single_listing(self, listing_id: int):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEtsySingleListing, listing_id=listing_id,
        )
        return objects["results"]

    def get_listing_attributes(self, listing_id: int):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEtsyListingAttibuteList, listing_id=listing_id,
        )
        return {"attributes": objects["results"]}

    def get_listing_products(self, listing_id: int):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEtsyListingProductList, listing_id=listing_id,
        )
        return objects["results"]

    def make_request(self, listing_id: int, **kwargs):
        try:
            listing_data = self.get_single_listing(listing_id=listing_id)
            products_data = self.get_listing_products(listing_id=listing_id)
            attributes_data = self.get_listing_attributes(listing_id=listing_id)
        except self.exception_class as error:
            is_success = False
            errors = str(error)
            message = f"Не удалось получить листинг Etsy.\n{errors}"
            objects = {"errors": errors}
        else:
            is_success = True
            message = "Листинг Etsy и его вариации успешно получены."
            objects = {"results": {**listing_data, **products_data, **attributes_data}}
        return is_success, message, objects


class RemoteDownloadEtsyListing(RemoteGetEtsyListing):
    def success_trigger(self, **kwargs):
        is_success, message, objects = super().success_trigger(**kwargs)
        # TODO
        return is_success, message, objects
