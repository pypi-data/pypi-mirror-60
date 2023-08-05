from ebay.policy.serializers.payment_policy import BasePaymentPolicySerializer


class CreatePaymentPolicySerializer(BasePaymentPolicySerializer):
    class Meta(BasePaymentPolicySerializer.Meta):
        pass
