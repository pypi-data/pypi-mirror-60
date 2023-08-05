from ebay.order.actions.shipping_fulfillment import GetEbayShippingFulfillmentList
from ebay.order.models import EbayOrder
from ebay.order.serializers.shipping_fulfillment import (
    EbayShippingFulfillmentSerializer,
)
from rest_framework import mixins
from rest_framework.decorators import action

from zonesmart import remote_action_views, views


class EbayShippingFulfillmentViewSet(
    remote_action_views.RemoteActionResponseViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    views.GenericSerializerViewSet,
):
    serializer_classes = {
        "default": EbayShippingFulfillmentSerializer,
    }
    remote_api_actions = {"remote_download_list": GetEbayShippingFulfillmentList}

    def get_queryset(self):
        return super().get_queryset().filter(order__id=self.kwargs["order_id"])

    @action(detail=False)
    def remote_download_list(self, request, *args, **kwargs):
        order_id = self.kwargs["order_id"]
        order = EbayOrder.objects.get(id=order_id)
        return super().get_action_response(entity=order, ignore_status=True)
