from amazon.order.actions import DownloadAmazonOrderItems
from amazon.order.serializers.order_item import BaseAmazonOrderItemSerializer
from rest_framework import viewsets
from rest_framework.decorators import action

from zonesmart import remote_action_views


class AmazonOrderItemViewSet(
    remote_action_views.RemoteActionResponseViewSet, viewsets.ReadOnlyModelViewSet
):
    serializer_class = BaseAmazonOrderItemSerializer
    lookup_field = "id"
    remote_api_actions = {"remote_download_list": DownloadAmazonOrderItems}

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(
            order=self.kwargs["order_id"]
        )

    @action(detail=False, methods=["GET"])
    def remote_download_list(self, request, *args, **kwargs):
        action_call_kwargs = {"order_id": self.kwargs["order_id"]}
        return self.get_action_response(
            detail=False, action_call_kwargs=action_call_kwargs
        )
