from ebay.policy.serializers.return_policy import BaseReturnPolicySerializer
from rest_framework import serializers

from zonesmart.serializers import NotNullAndEmptyStringModelSerializer


class UpdateOrCreateReturnPolicySerializer(
    BaseReturnPolicySerializer, NotNullAndEmptyStringModelSerializer
):
    marketplaceId = serializers.CharField(source="channel.domain.code")

    class Meta:
        model = BaseReturnPolicySerializer.Meta.model
        exclude = [
            "id",
            "channel",
            "status",
            "created",
            "modified",
            "published_at",
            "returnMethod",
        ]
