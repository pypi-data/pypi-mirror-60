from ebay.policy.actions.fulfillment_policy import (
    RemoteDownloadFulfillmentPolicyList,
    UpdateFulfillmentPolicy,
    UploadFulfillmentPolicy,
    WithdrawFulfillmentPolicy,
)
from ebay.policy.filters import FulfillmentPolicyFilterSet
from ebay.policy.serializers.fulfillment_policy import (
    BaseFulfillmentPolicySerializer,
    CreateFulfillmentPolicySerializer,
    UpdateFulfillmentPolicySerializer,
)
from ebay.policy.views import PolicyViewSet


class FulfillmentPolicyViewSet(PolicyViewSet):
    """
    ViewSet for fulfillment policy model
    """

    remote_api_actions = {
        "remote_download_list": RemoteDownloadFulfillmentPolicyList,
        "remote_create": UploadFulfillmentPolicy,
        "remote_update": UpdateFulfillmentPolicy,
        "remote_delete": WithdrawFulfillmentPolicy,
    }
    serializer_classes = {
        "default": BaseFulfillmentPolicySerializer,
        "create": CreateFulfillmentPolicySerializer,
        "update": UpdateFulfillmentPolicySerializer,
        "partial_update": UpdateFulfillmentPolicySerializer,
    }
    filterset_class = FulfillmentPolicyFilterSet
