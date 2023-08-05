from etsy.account.models import EtsyUserAccount, EtsyUserAccountInfo
from rest_framework import serializers

from zonesmart.marketplace.serializers.marketplace_user_account import (
    MarketplaceUserAccountSerializer,
)


class EtsyUserAccountSerializer(serializers.ModelSerializer):
    marketplace_user_account = MarketplaceUserAccountSerializer(read_only=True)

    class Meta:
        model = EtsyUserAccount
        fields = "__all__"


class CreateEtsyUserAccountSerializer(serializers.ModelSerializer):
    oauth_token = serializers.CharField()
    oauth_verifier = serializers.CharField()

    class Meta:
        model = EtsyUserAccount
        fields = [
            "oauth_token",
            "oauth_verifier",
        ]


class FeedbackInfoSerializer(serializers.Serializer):
    count = serializers.IntegerField(source="feedback_count")
    score = serializers.IntegerField(source="feedback_score", allow_null=True)


class EtsyUserAccountInfoSerializer(serializers.ModelSerializer):
    feedback_info = FeedbackInfoSerializer()

    class Meta:
        model = EtsyUserAccountInfo
        exclude = ["etsy_account"]

    def update(self, instance, validated_data):
        feedback_info = validated_data.pop("feedback_info")
        return super().update(
            instance, validated_data={**validated_data, **feedback_info}
        )

    def create(self, validated_data):
        feedback_info = validated_data.pop("feedback_info")
        return super().create(validated_data={**validated_data, **feedback_info})
