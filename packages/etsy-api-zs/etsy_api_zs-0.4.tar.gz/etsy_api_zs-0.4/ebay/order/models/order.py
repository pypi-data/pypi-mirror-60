import json

from django.db import models

from ebay.data import enums

from zonesmart.marketplace.models import MarketplaceUserAccount
from zonesmart.models import UUIDModel


class EbayOrder(UUIDModel):
    marketplace_user_account = models.ForeignKey(
        MarketplaceUserAccount,
        on_delete=models.CASCADE,
        related_name="ebay_orders",
        related_query_name="ebay_order",
    )
    # Fields
    # Buyer
    # https://developer.ebay.com/api-docs/sell/fulfillment/types/sel:Buyer
    buyer_username = models.CharField(max_length=100, verbose_name="ID покупателя")
    buyerCheckoutNotes = models.CharField(
        max_length=200, blank=True, default="", verbose_name="Комментарии покупателя"
    )
    creationDate = models.DateTimeField(verbose_name="Дата и время создания заказа")
    ebayCollectAndRemitTax = models.BooleanField(
        blank=True, null=True, verbose_name="eBay взимает налог"
    )
    _fulfillment_hrefs = models.TextField(
        default="[]", verbose_name="Ссылки для вызова API (getShippingFulfillment)"
    )
    lastModifiedDate = models.DateTimeField(
        verbose_name="Дата и время последнего изменения заказа"
    )
    legacyOrderId = models.CharField(max_length=50, verbose_name="Legacy order ID")
    orderFulfillmentStatus = models.CharField(
        max_length=50,
        choices=enums.OrderFulfillmentStatus,
        verbose_name="Статус фулфилмента заказа",
    )
    orderId = models.CharField(max_length=50, verbose_name="ID заказа")
    orderPaymentStatus = models.CharField(
        max_length=50,
        choices=enums.OrderPaymentStatusEnum,
        verbose_name="Статус оплаты заказа",
    )
    salesRecordReference = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Sales record reference"
    )
    sellerId = models.CharField(max_length=100, verbose_name="ID продавца")

    def __str__(self):
        return self.orderId

    class Meta:
        verbose_name = "Заказ с eBay"
        verbose_name_plural = "Заказы с eBay"
        constraints = [
            models.UniqueConstraint(
                fields=["orderId", "legacyOrderId",],
                name="unique_order_id_and_legacy_order_id",
            )
        ]

    @property
    def fulfillment_hrefs(self):
        return json.loads(self._fulfillment_hrefs)

    @fulfillment_hrefs.setter
    def fulfillment_hrefs(self, value):
        self._fulfillment_hrefs = json.dumps(list(set(self.fulfillment_hrefs + value)))
