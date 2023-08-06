from ebay.api.ebay_action import EbayAccountAction
from ebay_api.sell.inventory import item, item_group
from requests import codes

from .base import EbayListingAction


class RemoteDeleteEbayProduct(EbayAccountAction):
    api_class = item.DeleteInventoryItem

    def get_path_params(self, product, **kwargs):
        kwargs["sku"] = product.sku
        return super().get_path_params(**kwargs)

    def make_request(self, product, **kwargs):
        is_success, message, objects = super().make_request(product=product, **kwargs)
        if kwargs.get("ignore_404", False) and ("response" in objects):
            if objects["response"].status_code == codes.not_found:
                is_success = True
                message = (
                    "Товар не может быть удалён, так как не существует "
                    f'(SKU: {self.path_params["sku"]}).'
                )
        return is_success, message, objects

    def success_trigger(self, message, objects, product, **kwargs):
        product.offerId = None
        product.listingId = None
        product.save()

        message = f"Товар был успешно удалён с eBay (SKU: {product.sku})."
        return super().success_trigger(message, objects, **kwargs)

    def failure_trigger(self, message, objects, product, **kwargs):
        message = f"Не удалось удалить товар из eBay (SKU: {product.sku}).\n{message}"
        return super().failure_trigger(message, objects, **kwargs)


class RemoteDeleteEbayProductGroup(EbayListingAction):
    api_class = item_group.DeleteInventoryItemGroup

    def get_path_params(self, **kwargs):
        kwargs["inventoryItemGroupKey"] = self.listing.listing_sku
        return super().get_path_params(**kwargs)

    def make_request(self, **kwargs):
        is_success, message, objects = super().make_request(**kwargs)
        if kwargs.get("ignore_404", False) and ("response" in objects):
            if objects["response"].status_code == codes.not_found:
                is_success = True
                message = (
                    "Группа товаров не может быть удалена, так как не существует "
                    f"(ID: {self.listing.listing_sku})."
                )
        return is_success, message, objects

    def success_trigger(self, message, objects, **kwargs):
        self.listing.groupListingId = None
        self.listing.save()
        return super().success_trigger(message, objects, **kwargs)


class RemoteDeleteEbayListing(EbayListingAction):
    description = "Удаление листинга с eBay"

    def remote_delete_product(self, **kwargs):
        return self.raisable_action(api_class=RemoteDeleteEbayProduct, **kwargs)

    def remote_delete_product_group(self, **kwargs):
        return self.raisable_action(api_class=RemoteDeleteEbayProductGroup, **kwargs)

    def make_request(self, ignore_404=True, **kwargs):
        try:
            # delete all variations
            if self.listing.products_num:
                for product in self.listing.products.all():
                    self.remote_delete_product(product=product, ignore_404=ignore_404)
            # delete group
            self.remote_delete_product_group(ignore_404=ignore_404)
        except self.exception_class as error:
            is_success = False
            message = (
                f"Не удалось удалить товар с eBay (SKU: {self.listing.sku}).\n{error}"
            )
        else:
            self.listing.published = False

            is_success = True
            message = f"Товар был успешно удалён с eBay (SKU: {self.listing.sku})."
        finally:
            self.listing.save()

        objects = {}
        return is_success, message, objects
