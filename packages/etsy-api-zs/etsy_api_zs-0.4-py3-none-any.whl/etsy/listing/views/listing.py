from etsy.listing.serializers.etsy_listing.base import BaseEtsyListingSerializer

from zonesmart.views import GenericSerializerModelViewSet


class EtsyListingViewSet(GenericSerializerModelViewSet):
    serializer_classes = {"default": BaseEtsyListingSerializer}
