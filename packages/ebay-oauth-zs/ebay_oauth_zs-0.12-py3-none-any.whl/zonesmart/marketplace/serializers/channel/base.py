from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from zonesmart.marketplace.models import Channel


class BaseChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ["id", "name", "domain", "marketplace_user_account"]
        read_only_fields = fields

    def validate(
        self, attrs
    ):  # добавить проверку, что domain.marketplace == marketplace_user_account.marketplace
        error_list = list()
        domain = attrs.get("domain")
        marketplace_user_account = attrs.get("marketplace_user_account")
        if domain and marketplace_user_account:
            if domain not in marketplace_user_account.marketplace.domains.all():
                error_list.append("Нельзя привязать выбранный домен к каналу продаж.")
            if Channel.objects.filter(
                marketplace_user_account=marketplace_user_account, domain=domain
            ).exists():
                error_list.append(
                    "Пользовательский канал продаж с таким доменом уже существует."
                )
        if error_list:
            raise ValidationError({"domain": error_list})
        return attrs
