from ebay.location.actions import (
    RemoteDownloadEbayLocations,
    RemoteUpdateEbayLocation,
    RemoteUploadEbayLocation,
    WithdrawEbayLocation,
)
from ebay.location.filters import EbayLocationFilterSet
from ebay.location.serializers import (
    BaseEbayLocationSerializer,
    UpdateEbayLocationSerializer,
)

from zonesmart import remote_action_views
from zonesmart.views import GenericSerializerModelViewSet


class EbayLocationViewSet(
    remote_action_views.RemoteDownloadListActionByMarketplaceAccount,
    remote_action_views.RemoteCreateAction,
    remote_action_views.RemoteDeleteAction,
    remote_action_views.RemoteUpdateAction,
    GenericSerializerModelViewSet,
):
    """
    ViewSet for ebay location model
    """

    remote_api_actions = {
        "remote_download_list": RemoteDownloadEbayLocations,
        "remote_create": RemoteUploadEbayLocation,
        "remote_delete": WithdrawEbayLocation,
        "remote_update": RemoteUpdateEbayLocation,
    }
    serializer_classes = {
        "default": BaseEbayLocationSerializer,
        "update": UpdateEbayLocationSerializer,
        "partial_update": UpdateEbayLocationSerializer,
    }
    filterset_class = EbayLocationFilterSet

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(marketplace_user_account__user=self.request.user)
        )
