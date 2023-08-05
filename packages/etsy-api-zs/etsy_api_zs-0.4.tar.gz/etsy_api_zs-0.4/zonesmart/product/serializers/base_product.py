from rest_framework import serializers

from zonesmart.product.models import BaseProduct
from zonesmart.product.serializers import ProductImageSerializer


class BaseProductSerializer(serializers.ModelSerializer):
    main_image = ProductImageSerializer(read_only=True)
    extra_images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = BaseProduct
        exclude = [
            "user",
        ]
        read_only_fields = [
            "created",
            "modified",
        ]
