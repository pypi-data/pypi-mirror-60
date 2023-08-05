from ebay.order.models import CancelRequest, CancelStatus
from rest_framework import serializers


class CancelRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancelRequest
        exclude = ["id", "cancel_status"]


class CancelStatusSerializer(serializers.ModelSerializer):
    cancelRequests = CancelRequestSerializer(many=True, source="cancel_requests")

    class Meta:
        model = CancelStatus
        exclude = ["id", "order"]
