from ebay.policy.actions.payment_policy import (
    RemoteDownloadPaymentPolicyList,
    UpdatePaymentPolicy,
    UploadPaymentPolicy,
    WithdrawPaymentPolicy,
)
from ebay.policy.filters import PaymentPolicyFilterSet
from ebay.policy.serializers.payment_policy import (
    BasePaymentPolicySerializer,
    CreatePaymentPolicySerializer,
    UpdatePaymentPolicySerializer,
)
from ebay.policy.views import PolicyViewSet


class PaymentPolicyViewSet(PolicyViewSet):
    """
    ViewSet for payment policy model
    """

    serializer_classes = {
        "default": BasePaymentPolicySerializer,
        "create": CreatePaymentPolicySerializer,
        "update": UpdatePaymentPolicySerializer,
        "partial_update": UpdatePaymentPolicySerializer,
    }
    remote_api_actions = {
        "remote_download_list": RemoteDownloadPaymentPolicyList,
        "remote_create": UploadPaymentPolicy,
        "remote_update": UpdatePaymentPolicy,
        "remote_delete": WithdrawPaymentPolicy,
    }
    filterset_class = PaymentPolicyFilterSet
