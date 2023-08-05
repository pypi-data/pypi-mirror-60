from zonesmart.support.serializers.support_request_message import (
    BaseSupportRequestMessageSerializer,
    CreateSupportRequestMessageSerializer,
    UpdateSupportRequestMessageSerializer,
)
from zonesmart.views import GenericSerializerModelViewSet


class SupportRequestMessageViewSet(GenericSerializerModelViewSet):
    serializer_classes = {
        "default": BaseSupportRequestMessageSerializer,
        "create": CreateSupportRequestMessageSerializer,
        "update": UpdateSupportRequestMessageSerializer,
    }

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(support_request_id=self.kwargs["support_request_id"])
        )

    def perform_create(self, serializer):
        serializer.save(
            support_request_id=self.kwargs["support_request_id"],
            author=self.request.user,
        )
