from etsy.account.models import EtsyUserAccount, EtsyUserAccountInfo
from etsy.api.etsy_action import EtsyAction, EtsyAccountAction
from etsy.api.etsy_api.actions.account import GetEtsyUserAccountInfo
from zonesmart.marketplace.models import (
    Channel,
    Domain,
    Marketplace,
    MarketplaceUserAccount,
)
from etsy.account.serializers.etsy_account import DownloadEtsyUserAccountInfoSerializer


class RemoteGetEtsyUserAccountToken(EtsyAction):
    def make_request(
        self,
        oauth_verifier: str,
        temp_access_token: str,
        temp_access_token_secret: str,
        **kwargs,
    ):
        try:
            token = self.get_user_token_data(
                oauth_verifier=oauth_verifier,
                temp_access_token=temp_access_token,
                temp_access_token_secret=temp_access_token_secret,
            )
        except self.exception_class as error:
            is_success = False
            message = f"Не удалось получить токен авторизации Etsy.\n{error}"
            objects = {"errors": error}
        else:
            is_success = True
            message = "Токен авторизации Etsy успешно получен."
            objects = {"results": {"token": token}}
        return is_success, message, objects


class CreateOrUpdateEtsyUserAccount(RemoteGetEtsyUserAccountToken):
    def success_trigger(self, message, objects, **kwargs):
        # TODO: check user account ID

        # Create marketplace user account
        marketplace_user_account = MarketplaceUserAccount.objects.create(
            user=self.request.user,
            marketplace=Marketplace.objects.get(unique_name="etsy"),
        )

        # Create Etsy user account
        token = objects["results"]["token"]
        etsy_account, created = EtsyUserAccount.objects.update_or_create(
            marketplace_user_account=marketplace_user_account,
            sandbox=self.is_sandbox,
            defaults={"access_token": token.key, "access_token_secret": token.secret,},
        )

        # Create channel
        channel, created = Channel.objects.update_or_create(
            marketplace_user_account=marketplace_user_account,
            domain=Domain.objects.get(code="ETSY"),
            defaults={"name": "Канал продаж Etsy"},
        )

        objects["results"].update(
            {
                "marketplace_user_account": marketplace_user_account,
                "etsy_account": etsy_account,
                "channel": channel,
            }
        )
        return super().success_trigger(message, objects, **kwargs)


class RemoteGetEtsyUserAccountInfo(EtsyAccountAction):
    api_class = GetEtsyUserAccountInfo


class DownloadEtsyUserAccountInfo(RemoteGetEtsyUserAccountInfo):
    def success_trigger(self, message, objects, **kwargs):
        print(message, objects, kwargs)
        if objects["params"]["user_id"] != "__SELF__":
            is_success = False
            message = "Нельзя сохранить информацию о другом пользователе"
        else:
            if objects["count"] != 1:
                is_success = False
                message = "Аккаунт не найден."
            else:
                serializer = DownloadEtsyUserAccountInfoSerializer(
                    data=objects["results"][0]
                )
                etsy_account = self.marketplace_user_account.marketplace_account
                try:
                    instance = EtsyUserAccountInfo.objects.get(
                        etsy_account=etsy_account
                    )
                except EtsyUserAccountInfo.DoesNotExist:
                    pass
                else:
                    serializer.instance = instance

                if serializer.is_valid():
                    serializer.save(etsy_account=etsy_account)
                    is_success = True
                else:
                    is_success = False
                    message = str(serializer.errors)
                    objects["errors"] = serializer.errors
        return is_success, message, objects
