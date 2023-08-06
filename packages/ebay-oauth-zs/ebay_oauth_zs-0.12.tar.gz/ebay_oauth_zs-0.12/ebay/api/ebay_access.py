from urllib import parse

from django.conf import settings

from ebay.account.models import EbayAppAccount
from ebay_oauth.credentialutil import credentials as Credentials
from ebay_oauth.model import environment
from ebay_oauth.oauth_client import EbayOAuthClient

from zonesmart.marketplace.api.marketplace_access import MarketplaceAPIAccess
from zonesmart.utils.logger import get_logger

logger = get_logger(__name__)


class EbayAPIAccessError(Exception):
    pass


class EbayAPIAccess(MarketplaceAPIAccess):
    marketplace_name = "eBay"

    @property
    def is_sandbox(self):
        return settings.EBAY_SANDBOX

    @property
    def oauth_env(self):
        if self.is_sandbox:
            return environment.SANDBOX
        else:
            return environment.PRODUCTION

    @property
    def app_api_scopes(self):
        if self.is_sandbox:
            return settings.APP_SANDBOX_API_SCOPES
        else:
            return settings.APP_PRODUCTION_API_SCOPES

    @property
    def user_api_scopes(self):
        if self.is_sandbox:
            return settings.USER_SANDBOX_API_SCOPES
        else:
            return settings.USER_PRODUCTION_API_SCOPES

    @property
    def credentials(self):
        if not getattr(self, "credentials_", None):
            if self.is_sandbox:
                config = settings.EBAY_APP_CONFIG["sandbox"]
            else:
                config = settings.EBAY_APP_CONFIG["production"]
            self.credentials_ = Credentials(**config)
        return self.credentials_

    @property
    def client(self):
        return EbayOAuthClient(env_type=self.oauth_env, credentials=self.credentials,)

    def get_auth_url(self, state=None):
        url = self.client.generate_user_authorization_url(
            scopes=self.user_api_scopes, state=state,
        )
        return url

    def get_user_token_data(self, code: str, decode: bool = True):
        if decode:
            code = parse.unquote(code)
        return self.client.exchange_code_for_access_token(code=code)

    def get_app_token_data(self):
        return self.client.get_application_access_token(scopes=self.app_api_scopes,)

    def get_refreshed_token_data(self, refresh_token: str = ""):
        if not refresh_token:
            return self.get_app_token_data()
        else:
            return self.client.get_user_access_token(
                refresh_token=refresh_token, scopes=self.user_api_scopes,
            )

    @property
    def app_account_instance(self):
        return EbayAppAccount.objects.get_or_create(sandbox=self.is_sandbox)[0]

    def set_account(self, **kwargs):
        account = super().set_account(**kwargs)

        if self.is_sandbox != account.sandbox:
            message = (
                f"settings.EBAY_SANDBOX != marketplace_user_account.marketplace_account.sandbox"
                f" ({self.is_sandbox} != {account.sandbox})."
            )
            logger.error(message)
            raise EbayAPIAccessError(message)

        return account
