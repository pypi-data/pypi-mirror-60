from ebay.policy.serializers.return_policy import BaseReturnPolicySerializer


class CreateReturnPolicySerializer(BaseReturnPolicySerializer):
    class Meta(BaseReturnPolicySerializer.Meta):
        pass

    def create(self, validated_data):
        if not validated_data.get("categoryTypes"):
            validated_data["categoryTypes"] = [
                {"name": "ALL_EXCLUDING_MOTORS_VEHICLES", "default": False}
            ]
        return self.Meta.model.objects.create(**validated_data)
