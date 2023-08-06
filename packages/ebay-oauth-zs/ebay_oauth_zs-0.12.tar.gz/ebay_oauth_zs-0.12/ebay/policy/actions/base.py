from django.db import IntegrityError

from ebay.api.ebay_action import EbayChannelAction, EbayEntityAction
from rest_framework.exceptions import ValidationError


class GetPolicyAction(EbayChannelAction):
    description = "Получение политики eBay"
    by_name_api_class = None
    by_id_api_class = None
    path_param_name = None

    def make_request(self, *args, **kwargs):
        name = kwargs.get("name", None)
        policy_id = kwargs.get("policy_id", None)

        if bool(name) == bool(policy_id):
            raise AttributeError(
                'Необходимо задать либо аргумент "name", либо аргумент "policy_id".'
            )
        elif name:
            self.api_class = self.by_name_api_class
            kwargs.update(
                {"name": name, "marketplace_id": self.marketplace_id,}
            )
        elif policy_id:
            self.api_class = self.by_id_api_class
            kwargs.update({self.path_param_name: policy_id})

        return super().make_request(*args, **kwargs)


class RemoteDownloadPolicyAction(EbayChannelAction):
    description = "Получение и сохранение политики с eBay"
    policy_id_key = None
    serializer = None
    unique_name = None

    def success_trigger(self, message: str, objects: dict, **kwargs):
        policy_data = objects["results"]

        policy_data["policy_id"] = policy_data.pop(self.policy_id_key)
        policy_data["channel"] = self.channel.id
        policy_data["status"] = self.serializer.Meta.model.STATUS.published

        serializer = self.serializer(data=policy_data)
        serializer.is_valid(raise_exception=True)

        # Try to save and handle UniqueConstraint model errors
        try:
            serializer.save()
        except IntegrityError as e:
            error_args = str(e.args)
            if f"unique_{self.unique_name}_policy_name" in error_args:
                raise ValidationError(
                    "Политика с таким именем уже была загружена ранее"
                )
            elif f"unique_{self.unique_name}_policy_id" in error_args:
                raise ValidationError("Политика с таким ID уже была загружена ранее")

        return super().success_trigger(message=message, objects=objects)


class GetPolicyListAction(EbayChannelAction):
    description = "Получение всех политик с eBay"
    api_class = None

    def get_query_params(self, **kwargs):
        kwargs["marketplace_id"] = self.marketplace_id
        return super().get_query_params(**kwargs)


class RemoteDownloadPolicyListAction(EbayChannelAction):
    description = "Получение и сохранение политик с eBay"
    objects_data_list_key = None
    policy_id_key = None
    serializer = None
    unique_name = None

    def success_trigger(self, message: str, objects: dict, *args, **kwargs):
        policy_data_list = objects["results"][self.objects_data_list_key]

        for policy_data in policy_data_list:
            policy_id = policy_data.pop(self.policy_id_key)
            policy_data["channel"] = self.channel.id
            try:
                instance = self.serializer.Meta.model.objects.get(policy_id=policy_id)
                serializer = self.serializer(instance=instance, data=policy_data)
            except self.serializer.Meta.model.DoesNotExist:
                serializer = self.serializer(data=policy_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(policy_id=policy_id, status="published")

        return super().success_trigger(message=message, objects=objects)


class UploadPolicyAction(EbayEntityAction):
    description = "Загрузка политики на eBay"
    api_class = None
    payload_serializer = None


class UpdatePolicyAction(EbayEntityAction):
    description = "Обновление политики на eBay"
    path_param = None
    api_class = None
    payload_serializer = None

    def get_path_params(self, **kwargs):
        kwargs[self.path_param] = self.policy.policy_id
        return super().get_path_params(**kwargs)


class WithdrawPolicyAction(EbayEntityAction):
    description = "Удаление политики с eBay"
    path_param = None
    api_class = None

    def get_path_params(self, **kwargs):
        kwargs[self.path_param] = self.policy.policy_id
        return super().get_path_params(**kwargs)
