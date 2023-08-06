from amazon.account.serializers.amazon_user_account import (
    BaseAmazonUserAccountSerializer,
)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from zonesmart.marketplace.models import Marketplace, MarketplaceUserAccount


class CreateAmazonUserAccountSerializer(BaseAmazonUserAccountSerializer):
    marketplace = serializers.PrimaryKeyRelatedField(
        queryset=Marketplace.amazon.all(), write_only=True
    )

    class Meta(BaseAmazonUserAccountSerializer.Meta):
        fields = BaseAmazonUserAccountSerializer.Meta.fields + ["marketplace"]
        read_only_fields = [
            "id",
            "marketplace_user_account",
        ]

    def validate_access_token(self, value):
        if self.Meta.model.objects.filter(access_token=value).exists():
            raise ValidationError(f"Аккаунт с токеном доступа {value} уже создан.")
        return value

    def create(self, validated_data):
        # Create MarketplaceUserAccount
        marketplace_user_account = MarketplaceUserAccount.objects.create(
            user=validated_data["user"], marketplace=validated_data["marketplace"],
        )
        # Create AmazonUserAccount
        return self.Meta.model.objects.create(
            marketplace_user_account=marketplace_user_account,
            access_token=validated_data["access_token"],
        )
