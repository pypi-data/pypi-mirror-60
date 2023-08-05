from etsy.listing.models import EtsyListing, EtsyProduct, EtsyProductProperty
from rest_framework import serializers


class EtsyProductPropertySerializer(serializers.ModelSerializer):
    values = serializers.CharField(source="value_ids")

    class Meta:
        model = EtsyProductProperty
        fields = [
            "property_id",
            "values",
        ]


class EtsyProductSerializer(serializers.ModelSerializer):
    properties = EtsyProductPropertySerializer(many=True)

    class Meta:
        model = EtsyProduct
        fields = [
            "sku",
            "price",
            "quantity",
            "properties",
        ]


class EtsyListingSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(source="total_quantity")
    category = serializers.IntegerField(source="category.category_id")
    products = EtsyProductSerializer(many=True)

    class Meta:
        model = EtsyListing
        fields = [
            "quantity",
            "price",
            "title",
            "description",
            "category",
            "who_made",
            "when_made",
            "is_supply",
            "products",
        ]
