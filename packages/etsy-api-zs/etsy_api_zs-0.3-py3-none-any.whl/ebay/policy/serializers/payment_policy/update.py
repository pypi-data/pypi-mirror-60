from ebay.policy.serializers.payment_policy import BasePaymentPolicySerializer


class UpdatePaymentPolicySerializer(BasePaymentPolicySerializer):
    class Meta(BasePaymentPolicySerializer.Meta):
        read_only_fields = BasePaymentPolicySerializer.Meta.read_only_fields + [
            "channel",
            "policy_id",
        ]
