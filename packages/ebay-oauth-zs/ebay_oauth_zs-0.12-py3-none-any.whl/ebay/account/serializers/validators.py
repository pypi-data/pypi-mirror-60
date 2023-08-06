from django.contrib.auth import get_user_model
from django.utils import timezone

from ebay.account.models import EbayUserAccountProfile
from ebay.api.ebay_access import EbayAPIAccess
from ebay_api.commerce.identity import GetUser
from ebay_api.sell.account import GetPrivileges
from ebay_oauth.oauth_client import EbayOAuthClientError
from rest_framework.exceptions import ValidationError

User = get_user_model()


class EbayUserAccountValidator:
    def __init__(self, code: str, user: User):
        self.code = code
        self.user = user
        self.is_sandbox = False
        self.token_data = self.__get_token_data()
        self.access_token = self.token_data["access_token"]
        self.refresh_token = self.token_data["refresh_token"]
        self.user_results = None
        self.privileges_results = None
        self.validated = False
        self.profile = None

    def __get_token_data(self) -> dict:
        api = EbayAPIAccess()
        self.is_sandbox = api.is_sandbox
        try:
            token = api.get_user_token_data(self.code)
            token_data = token.token_dict
            token_data["access_token_expiry"] = timezone.make_aware(
                token_data["access_token_expiry"]
            )
            token_data["refresh_token_expiry"] = timezone.make_aware(
                token_data["refresh_token_expiry"]
            )
            return token_data
        except EbayOAuthClientError as err:
            raise ValidationError({"EbayOAuthClientError": str(err)})

    def validate_user(self):
        api = GetUser(access_token=self.access_token, sandbox=self.is_sandbox)
        is_success, message, objects = api.make_request()
        if is_success:
            user_id = objects["results"]["userId"]
            qs = EbayUserAccountProfile.objects.filter(userId=user_id)
            if qs.exists():
                profile: EbayUserAccountProfile = qs.first()
                if profile.ebay_user_account.user.id == self.user.id:
                    self.profile = profile
                else:
                    raise ValidationError(
                        {
                            "user_id": "Аккаунт уже был добавлен в систему другим пользователем."
                        }
                    )
            return objects["results"]
        raise ValidationError({"userId": message})

    def validate_privileges(self):
        api = GetPrivileges(access_token=self.access_token, sandbox=self.is_sandbox)
        is_success, message, objects = api.make_request()
        if is_success:
            results = objects["results"]
            registration_completed = results["sellerRegistrationCompleted"]
            if not registration_completed:
                raise ValidationError(
                    {
                        "sellerRegistrationCompleted": (
                            "Регистрация аккаунта продавца на eBay не была завершена. "
                            "Для добавления аккаунта необходимо завершить регистрацию в системе eBay."
                        )
                    }
                )
            return results
        raise ValidationError({"sellerRegistrationCompleted": message})

    def is_valid(self) -> bool:
        self.privileges_results = self.validate_privileges()
        self.user_results = self.validate_user()
        self.validated = True
        return True

    def get_results(self):
        assert (
            self.validated
        ), "Validation is not successfull or is_valid didnt called yet."
        return {"user": self.user_results, "privileges": self.privileges_results}
