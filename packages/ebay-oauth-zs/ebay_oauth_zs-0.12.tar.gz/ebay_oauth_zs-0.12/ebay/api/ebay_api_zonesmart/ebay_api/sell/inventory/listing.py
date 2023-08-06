from .base import InventoryAPI


class BulkMigrateListing(InventoryAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/inventory/resources/listing/methods/bulkMigrateListing
    """

    resource = ""
    method_type = "POST"
    url_postfix = "bulk_migrate_listing"
