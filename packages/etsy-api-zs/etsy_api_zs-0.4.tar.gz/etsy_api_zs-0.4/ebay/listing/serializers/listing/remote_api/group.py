from ebay.listing.models import EbayListing
from rest_framework import serializers

from zonesmart.serializers import ModelSerializerWithoutNullAndEmptyObjects


class GroupSerializer(ModelSerializerWithoutNullAndEmptyObjects):
    description = serializers.CharField(source="listing_description")
    inventoryItemGroupKey = serializers.CharField(source="listing_sku")
    aspects = serializers.SerializerMethodField()

    class Meta:
        model = EbayListing
        fields = ["description", "inventoryItemGroupKey", "title", "aspects"]

    def get_aspects(self, instance: EbayListing):
        aspects = instance.aspects.all()
        data = dict()
        if aspects.exists():
            for aspect in aspects.values_list("name", "value", named=True):
                name = aspect.name
                value = aspect.value
                if aspect.name not in data:
                    data[name] = [value]
                else:
                    data[name].append(value)
        return data

    def to_representation(self, instance: EbayListing):
        representation = super().to_representation(instance)
        representation["variantSKUs"] = list(
            instance.products.all().values_list("sku", flat=True)
        )
        specifications_representation = dict()
        for specification_data in instance.products.values(
            "specification__name", "specification__value"
        ):
            name = specification_data["specification__name"]
            value = specification_data["specification__value"]
            specifications_representation[name] = specifications_representation.get(
                name, list()
            ) + [value]
        representation["variesBy"] = {
            "specifications": [
                {"name": name, "values": list(set(values))}
                for name, values in specifications_representation.items()
            ]
        }
        return representation
