from etsy.api.etsy_access import EtsyAPIAccess, EtsyAPIAccessError

from zonesmart.marketplace.api.marketplace_action import (
    MarketplaceAccountAction,
    MarketplaceAction,
    MarketplaceEntityAction,
)


class EtsyActionError(EtsyAPIAccessError):
    response = None


class EtsyAction(EtsyAPIAccess, MarketplaceAction):
    description = "Действие Etsy"
    exception_class = EtsyActionError
    api_method = None

    def str_to_int_params_conversion(self, params):
        for key, value in params.items():
            if isinstance(value, str) and key.endswith("_id"):
                try:
                    params[key] = int(value)
                except ValueError:
                    pass
        return params

    def filter_params(self, kwargs):
        return {
            param: kwargs[param]
            for param in self.api_class.params
            if kwargs.get(param, None) or (type(kwargs.get(param, None)) in [bool, int])
        }

    def get_params(self, **kwargs):
        if "user_id" in self.api_class.params:
            kwargs["user_id"] = kwargs.get("user_id", "__SELF__")

        if "shop_id" in self.api_class.params:
            if (not kwargs.get("shop_id", None)) and self.channel:
                if getattr(self.channel, "shop", None):
                    kwargs["shop_id"] = self.channel.shop.shop_id

        kwargs = self.str_to_int_params_conversion(kwargs)
        params = self.filter_params(kwargs)
        return params

    def make_request(self, **kwargs):
        if not getattr(self, "api_class", None):
            raise AttributeError("Необходимо задать атрибут 'api_class'.")

        if self.client.token:
            client = self.client
            api_key = ""
        else:
            client = None
            api_key = self.credentials["api_key"]

        api = self.api_class(
            api_key=api_key,
            oauth_client=client,
            oauth_env=self.oauth_env,
            # sandbox=self.is_sandbox,
        )

        params = self.get_params(**kwargs)

        return api.make_request(**params)


class EtsyAccountAction(EtsyAction, MarketplaceAccountAction):
    pass


class EtsyEntityAction(EtsyAction, MarketplaceEntityAction):
    publish_final_status = None

    def success_trigger(self, message, objects, **kwargs):
        if getattr(self, "publish_final_status", None) is not None:
            if getattr(self, "entity", None):
                self.entity.published = self.publish_final_status
                self.entity.save()
        return super().success_trigger(message, objects, **kwargs)
