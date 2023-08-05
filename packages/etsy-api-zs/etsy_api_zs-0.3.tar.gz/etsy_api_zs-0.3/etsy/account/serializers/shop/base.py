from etsy.account.models import EtsyShop, EtsyShopSection
from rest_framework import serializers


class EtsyShopSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtsyShopSection
        fields = ["shop_section_id", "title", "active_listing_count"]


class BaseEtsyShopSerializer(serializers.ModelSerializer):
    sections = EtsyShopSectionSerializer(required=False, many=True)

    class Meta:
        model = EtsyShop
        exclude = ["id", "channel"]
