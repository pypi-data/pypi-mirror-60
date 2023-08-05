from rest_framework import serializers

from zonesmart.marketplace.models import Domain


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ["id", "marketplace", "name", "description", "url"]
