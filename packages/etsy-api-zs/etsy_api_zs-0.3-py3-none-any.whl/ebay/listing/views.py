from ebay.listing.actions import (  # , RemoteCreateEbayListing, RemoteUpdateEbayListing
    RemoteDeleteEbayListing,
    SyncEbayListing,
)
from ebay.listing.serializers.listing.base import BaseEbayListingSerializer
from ebay.listing.serializers.listing.create import CreateEbayListingSerializer
from ebay.listing.serializers.listing.update import UpdateEbayListingSerializer

from zonesmart import remote_action_views
from zonesmart.views import GenericSerializerModelViewSet


class EbayListingViewSet(
    remote_action_views.RemoteDeleteAction,
    remote_action_views.RemoteSyncAction,
    GenericSerializerModelViewSet,
):
    remote_api_actions = {
        "remote_sync": SyncEbayListing,
        "remote_delete": RemoteDeleteEbayListing,
    }
    serializer_classes = {
        "default": BaseEbayListingSerializer,
        "update": UpdateEbayListingSerializer,
        "partial_update": UpdateEbayListingSerializer,
        "create": CreateEbayListingSerializer,
    }

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(channel__marketplace_user_account__user=self.request.user)
        )
