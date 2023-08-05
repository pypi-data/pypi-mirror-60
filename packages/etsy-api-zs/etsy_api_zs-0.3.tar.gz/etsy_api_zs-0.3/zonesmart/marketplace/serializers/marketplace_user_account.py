from rest_framework import serializers

from zonesmart.marketplace.models import MarketplaceUserAccount


class MarketplaceUserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketplaceUserAccount
        fields = "__all__"
