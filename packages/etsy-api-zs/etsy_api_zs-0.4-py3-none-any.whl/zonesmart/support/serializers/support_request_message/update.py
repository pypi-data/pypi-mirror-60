from zonesmart.support.serializers.support_request_message import (
    BaseSupportRequestMessageSerializer,
)


class UpdateSupportRequestMessageSerializer(BaseSupportRequestMessageSerializer):
    class Meta(BaseSupportRequestMessageSerializer.Meta):
        read_only_fields = [
            "id",
            "created",
            "author",
            "reply_to",
            "files",
        ]
