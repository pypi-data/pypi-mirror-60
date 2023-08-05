from rest_framework import serializers


class AbstractCategoryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = ["default", "name"]


class AbstractPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = [
            "id",
            "channel",
            "description",
            "name",
            "policy_id",
            "status",
            "categoryTypes",
        ]
        read_only_fields = ["id", "status", "policy_id"]

    def update(self, instance, validated_data):
        instance, created = self.Meta.model.objects.update_or_create(
            policy_id=instance.policy_id, defaults=validated_data
        )
        # Extra save for status update
        instance.save()
        return instance

    def create(self, validated_data):
        instance = self.Meta.model.objects.create(**validated_data)
        # Extra save for status update
        instance.save()
        return instance
