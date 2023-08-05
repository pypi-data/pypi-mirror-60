from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from zonesmart.support.models import SupportRequest, SupportRequestMessage
from zonesmart.support.serializers import SupportRequestMessageFileSerializer

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
        ]


class BaseSupportRequestMessageSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    files = SupportRequestMessageFileSerializer(required=False, many=True)

    class Meta:
        model = SupportRequestMessage
        fields = [
            "id",
            "created",
            "author",
            "reply_to",
            "message",
            "files",
        ]
        read_only_fields = fields

    def create(self, validated_data):
        reply_to = validated_data.get("reply_to", None)
        support_request_id = validated_data["support_request_id"]
        # Check if reply to message from current support request
        if reply_to:
            if reply_to not in SupportRequestMessage.objects.filter(
                support_request_id=support_request_id
            ):
                raise ValidationError(
                    {"reply_to": f"Сообщение с id {reply_to.id} не найдено в диалоге"}
                )
        if not SupportRequest.objects.filter(
            id=support_request_id,
            status__in=["NEW", "WAITING_FOR_HELPER", "WAITING_FOR_USER",],
        ).exists():
            raise ValidationError(
                {"support_request": "Вы не можете добавить сообщение в закрытый запрос"}
            )
        return super().create(validated_data)
