from ebay.api.ebay_action import EbayAccountAction, EbayEntityAction
from ebay.order.models import EbayShippingFulfillment
from ebay.order.serializers.api.download import (
    EbayShippingFulfillmentDownloadSerializer,
)
from ebay_api.sell.fulfillment import shipping_fulfillment as fulfillment_api


class UploadEbayShippingFulfillment(EbayEntityAction):
    description = "Создание фулфилмента заказа eBay"
    entity_name = "shipping_fulfillment"
    entity_model = EbayShippingFulfillment
    api_class = fulfillment_api.CreateShippingFulfillment
    payload_serializer = None

    def get_path_params(self, **kwargs):
        kwargs["orderId"] = self.shipping_fulfillment.orderId
        return super().get_path_params(**kwargs)


class GetEbayShippingFulfillmentList(EbayAccountAction):
    description = "Получение всех фулфилментов заказа eBay"
    api_class = fulfillment_api.GetShippingFulfillments

    def success_trigger(self, message: str, objects: dict, **kwargs):
        serializer = EbayShippingFulfillmentDownloadSerializer(
            data=objects["results"]["fulfillments"], many=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(order=self.entity)
        return super().success_trigger(message, objects, **kwargs)


class RemoteDownloadEbayShippingFulfillmentList(GetEbayShippingFulfillmentList):
    description = "Получение и сохранение всех фулфилментов заказа eBay"

    def success_trigger(self, message, objects, **kwargs):
        return super().success_trigger(message, objects, **kwargs)


class GetEbayShippingFulfillment(EbayAccountAction):
    description = "Получение фулфилмента заказа eBay"
    api_class = fulfillment_api.GetShippingFulfillment
