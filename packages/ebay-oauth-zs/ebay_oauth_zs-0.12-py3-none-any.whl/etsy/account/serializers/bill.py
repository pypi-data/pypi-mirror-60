from django.utils import timezone
from rest_framework import serializers

from etsy.account.models.bill import EtsyBillCharge, EtsyUserBillingOverview


class EtsyBillChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtsyBillCharge
        exclude = ["bill_charge_id", "etsy_user_account"]


class EtsyUserBillingOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtsyUserBillingOverview
        exclude = ["id", "etsy_user_account"]


class DownloadEtsyBillChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtsyBillCharge
        exclude = ["etsy_user_account"]
        extra_kwargs = {"bill_charge_id": {"validators": []}}

    def to_internal_value(self, data):
        # Format timestamp income datetime into django
        for time_key in ["creation_tsz", "last_modified_tsz"]:
            tz = data.pop(time_key, None)
            if tz:
                data[time_key] = timezone.make_aware(
                    timezone.datetime.fromtimestamp(tz)
                )
        # Rename Etsy default fields for local model fields
        typ = data.pop("type", None)
        type_id = data.pop("type_id", None)
        if typ:
            data["bill_type"] = typ
        if type_id:
            data["bill_type_id"] = type_id
        # Return dataßß
        return super().to_internal_value(data)

    def create(self, validated_data):
        etsy_user_account = validated_data.pop("etsy_user_account")
        bill_charge_id = validated_data.pop("bill_charge_id")
        instance, created = self.Meta.model.objects.update_or_create(
            etsy_user_account=etsy_user_account,
            bill_charge_id=bill_charge_id,
            defaults=validated_data,
        )
        return instance


class DownloadEtsyUserBillingOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtsyUserBillingOverview
        exclude = ["etsy_user_account"]

    def to_internal_value(self, data):
        date_due = data.pop("date_due", None)
        if date_due:
            data["date_due"] = timezone.make_aware(
                timezone.datetime.fromtimestamp(date_due)
            )
        return super().to_internal_value(data)

    def create(self, validated_data):
        etsy_user_account = validated_data.pop("etsy_user_account")
        instance, created = self.Meta.model.objects.update_or_create(
            etsy_user_account=etsy_user_account, defaults=validated_data
        )
        return instance
