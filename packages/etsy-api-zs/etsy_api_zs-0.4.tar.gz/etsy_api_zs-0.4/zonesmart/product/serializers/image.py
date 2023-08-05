from rest_framework import serializers

from zonesmart.product.models import ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source="get_url", read_only=True)
    image_file = serializers.ImageField(write_only=True)

    class Meta:
        model = ProductImage
        fields = ["id", "url", "description", "image_file"]
        read_only_fields = ["id"]
