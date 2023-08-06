from etsy.api.etsy_action import EtsyAccountAction


class FindAllShopTransactions(EtsyAccountAction):
    """
    Retrieves a set of Transaction objects associated to a Shop.

    Docs:
    https://www.etsy.com/developers/documentation/reference/transaction#method_findallshoptransactions
    """

    api_method = "findAllShopTransactions"
    params = ["shop_id"]


class FindAllShopReceiptTransactions(EtsyAccountAction):
    """
    Retrieves a set of Transaction objects associated to a Shop_Receipt2.

    Docs:
    https://www.etsy.com/developers/documentation/reference/transaction#method_findallshop_receipt2transactions
    """

    api_method = "findAllShop_Receipt2Transactions"
    params = ["receipt_id"]
