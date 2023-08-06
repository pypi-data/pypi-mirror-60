from rest_framework import serializers

from zonesmart.support.models import SupportRequest


class BaseSupportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequest
        fields = [
            "created",
            "id",
            "creator",
            "helper",
            "status",
            "status_changed",
            "title",
        ]
        read_only_fields = [
            "created",
            "id",
            "creator",
            "helper",
            "status",
            "status_changed",
        ]
