from ebay.listing.models import EbayProduct, EbayProductSpecification
from rest_framework import serializers

from zonesmart.product.models import ProductImage
from zonesmart.product.serializers import ProductImageSerializer


class BaseEbayProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EbayProductSpecification
        exclude = ["id", "product"]


class BaseEbayProductSerializer(serializers.ModelSerializer):
    specifications = BaseEbayProductSpecificationSerializer(
        required=False, many=True, allow_null=False
    )
    main_image = serializers.PrimaryKeyRelatedField(queryset=ProductImage.objects.all())

    class Meta:
        model = EbayProduct
        exclude = ["id", "listing"]

    def to_internal_value(self, data):
        if "specifications" in data:
            data["specifications"] = [
                {"name": name, "value": value}
                for name, value in data["specifications"].items()
            ]
        return super().to_internal_value(data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if "specifications" in representation:
            representation["specifications"] = {
                specification["name"]: specification["value"]
                for specification in representation["specifications"]
            }
        representation["main_image"] = ProductImageSerializer(
            instance=instance.main_image
        ).data
        return representation
