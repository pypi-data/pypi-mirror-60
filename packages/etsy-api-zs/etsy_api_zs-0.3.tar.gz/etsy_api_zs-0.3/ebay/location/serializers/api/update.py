from ebay.location.models import EbayLocation

from zonesmart.serializers import NotNullAndEmptyStringModelSerializer


class UpdateEbayLocationSerializer(NotNullAndEmptyStringModelSerializer):
    class Meta:
        model = EbayLocation
        fields = [
            "name",
            "phone",
            "locationWebUrl",
            "locationInstructions",
            "locationAdditionalInformation",
        ]
