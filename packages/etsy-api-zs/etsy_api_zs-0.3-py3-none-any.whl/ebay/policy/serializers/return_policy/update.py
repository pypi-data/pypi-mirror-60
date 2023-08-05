from ebay.policy.serializers.return_policy import BaseReturnPolicySerializer


class UpdateReturnPolicySerializer(BaseReturnPolicySerializer):
    class Meta(BaseReturnPolicySerializer.Meta):
        read_only_fields = BaseReturnPolicySerializer.Meta.read_only_fields + [
            "channel",
            "policy_id",
        ]
