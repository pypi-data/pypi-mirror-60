from ebay.api.ebay_trading_api_action import EbayTradingAPIAction


class GetEbayCategoryFeatures(EbayTradingAPIAction):
    # https://developer.ebay.com/devzone/xml/docs/reference/ebay/GetCategoryFeatures.html
    verb = "GetCategoryFeatures"

    def get_params(self, category_id=None, feature_ids=None, **kwargs):
        return {
            "AllFeaturesForCategory": False,
            "CategoryID": category_id,
            "FeatureID": feature_ids,
            "ViewAllNodes": True,
            "DetailLevel": "ReturnAll",
        }

    def success_trigger(self, message, objects, **kwargs):
        objects["results"] = objects["results"].get("Category", [])
        if not objects["results"]:
            message = (
                f'Категория с заданным ID не существует (ID: {kwargs["category_id"]}).'
            )
            return super().failure_trigger(message, objects, **kwargs)
        return super().success_trigger(message, objects, **kwargs)


class GetTransportCategoryAspectsVS(EbayTradingAPIAction):
    # https://developer.ebay.com/devzone/xml/docs/reference/ebay/GetCategorySpecifics.html
    verb = "GetCategorySpecifics"

    def get_params(self, category_id, **kwargs):
        return {
            "CategoryID": category_id,
        }

    def make_request(self, *args, **kwargs):
        kwargs["domain_code"] = "EBAY_MOTORS_US"
        return super().make_request(*args, **kwargs)
