from amazon.account.models import AmazonUserAccount
from rest_framework import serializers


class BaseAmazonUserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmazonUserAccount
        fields = ["id", "marketplace_user_account", "access_token"]
        read_only_fields = fields
