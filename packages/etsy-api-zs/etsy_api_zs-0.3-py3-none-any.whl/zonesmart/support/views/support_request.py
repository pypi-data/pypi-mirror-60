from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from zonesmart.permissions import SupportGroupPermission
from zonesmart.support.models import SupportRequest
from zonesmart.support.serializers.support_request import (
    BaseSupportRequestSerializer,
    CreateSupportRequestSerializer,
)
from zonesmart.views import GenericSerializerViewSet


class SupportRequestViewSet(
    mixins.CreateModelMixin, GenericSerializerViewSet, viewsets.ReadOnlyModelViewSet
):
    serializer_classes = {
        "default": BaseSupportRequestSerializer,
        "create": CreateSupportRequestSerializer,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        # Return support requests for helper if support group exists for user
        if self.request.user.groups.filter(name="support").exists():
            return qs.filter(helper=self.request.user)
        # Or return support requests for creator by request user
        return qs.filter(creator=self.request.user)

    def perform_create(self, serializer):
        """
        Saves support request with user from request
        """
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=["POST"])
    def close(self, request, *args, **kwargs):
        """
        Closes support request.
        """
        instance: SupportRequest = self.get_object()
        # Check support request status
        if instance.status in [
            instance.STATUS.CLOSED_BY_USER,
            instance.STATUS.CLOSED_BY_TIMEOUT,
        ]:
            return Response(data=instance.status, status=status.HTTP_400_BAD_REQUEST)
        else:
            instance.status = instance.STATUS.CLOSED_BY_USER
            instance.save()
            return Response(data="Successfully closed", status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def reopen(self, request, *args, **kwargs):
        """
        Reopens support request
        """
        instance: SupportRequest = self.get_object()
        if instance.status not in [
            instance.STATUS.CLOSED_BY_USER,
            instance.STATUS.CLOSED_BY_TIMEOUT,
        ]:
            return Response(data=instance.status, status=status.HTTP_400_BAD_REQUEST)
        else:
            instance.status = instance.STATUS.NEW
            instance.helper = None
            instance.save()
            return Response(data="Successfully reopened", status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], permission_classes=[SupportGroupPermission])
    def take_to_work(
        self, request, *args, **kwargs
    ):  # добавить возможность выбора заявки?
        """
        Takes first support request for support group and saves request user as helper
        """
        support_request = BaseSupportRequestSerializer.Meta.model.objects.filter(
            helper__isnull=True
        ).first()
        if support_request:
            support_request.helper = self.request.user
            support_request.save()
            serializer = BaseSupportRequestSerializer(instance=support_request)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data="В очереди нет заявок.", status=status.HTTP_200_OK)
