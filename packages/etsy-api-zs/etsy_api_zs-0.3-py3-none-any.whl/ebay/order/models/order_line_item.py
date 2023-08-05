from django.db import models

from ebay.data import enums
from ebay.listing.models import EbayListing
from ebay.models.abstract import AbstractAmount
from ebay.order.models.order import EbayOrder


class EbayOrderLineItem(models.Model):
    order = models.ForeignKey(
        EbayOrder,
        on_delete=models.CASCADE,
        related_name="line_items",
        related_query_name="line_item",
        verbose_name="Заказ",
    )
    # Fields
    legacyItemId = models.CharField(max_length=100, verbose_name="Legacy ID товара")
    legacyVariationId = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Legacy ID товара из группы"
    )
    lineItemFulfillmentStatus = models.CharField(
        max_length=30,
        choices=enums.LineItemFulfillmentStatusEnum,
        verbose_name="Статус фулфилмента товара",
    )
    lineItemId = models.CharField(max_length=100, verbose_name="ID товара")
    listingMarketplaceId = models.CharField(
        max_length=30,
        choices=enums.MarketplaceEnum,
        verbose_name="Уникальный ID маркетплейса на котором продукт опубликован",
    )
    purchaseMarketplaceId = models.CharField(
        max_length=30,
        choices=enums.MarketplaceEnum,
        verbose_name="Уникальный ID маркетплейса на котором продукт опубликован",
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество единиц товара")
    # Optional when listing in the legacy/Trading API system, that's why it's default is random uuid4() value
    sku = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="SKU товара"
    )
    product = models.ForeignKey(
        EbayListing, on_delete=models.SET_NULL, blank=True, null=True,
    )
    soldFormat = models.CharField(
        max_length=30,
        choices=enums.SoldFormatEnum,
        verbose_name="Формат продажи товара",
    )
    title = models.CharField(max_length=100, verbose_name="Название товара")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Товар из заказа"
        verbose_name_plural = "Товары из заказа"


class AppliedPromotion(models.Model):
    line_item = models.ForeignKey(
        EbayOrderLineItem,
        on_delete=models.CASCADE,
        related_name="applied_promotions",
        related_query_name="applied_promotion",
    )
    # Fields
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    promotionId = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="ID акции на товар"
    )

    class Meta:
        verbose_name = "Акция на товар из заказа"
        verbose_name_plural = "Акции на товар из заказа"


class DiscountAmount(AbstractAmount):
    applied_promotion = models.OneToOneField(
        AppliedPromotion, on_delete=models.CASCADE, related_name="discount_amount"
    )

    class Meta:
        verbose_name = "Сумма скидки"
        verbose_name_plural = "Сумма скидок"


class LineItemDeliveryCost(models.Model):
    line_item = models.OneToOneField(
        EbayOrderLineItem, on_delete=models.CASCADE, related_name="delivery_cost"
    )


class ImportCharges(AbstractAmount):
    delivery_cost = models.OneToOneField(
        LineItemDeliveryCost, on_delete=models.CASCADE, related_name="import_charges"
    )


class ShippingCost(AbstractAmount):
    delivery_cost = models.OneToOneField(
        LineItemDeliveryCost, on_delete=models.CASCADE, related_name="shipping_cost"
    )


class ShippingIntermediationFee(AbstractAmount):
    delivery_cost = models.OneToOneField(
        LineItemDeliveryCost,
        on_delete=models.CASCADE,
        related_name="shipping_intermediation_fee",
    )


class DiscountedLineItemCost(AbstractAmount):
    line_item = models.OneToOneField(
        EbayOrderLineItem,
        on_delete=models.CASCADE,
        related_name="discounted_line_item_cost",
    )


class LineItemCost(AbstractAmount):
    line_item = models.OneToOneField(
        EbayOrderLineItem, on_delete=models.CASCADE, related_name="line_item_cost"
    )


class LineItemFulfillmentInstructions(models.Model):
    line_item = models.OneToOneField(
        EbayOrderLineItem,
        on_delete=models.CASCADE,
        related_name="line_item_fulfillment_instructions",
    )
    # Fields
    # This field is reserved for internal or future use
    destinationTimeZone = models.CharField(max_length=255, blank=True, null=True)
    guaranteedDelivery = models.BooleanField()
    maxEstimatedDeliveryDate = models.DateTimeField(blank=True, null=True)
    minEstimatedDeliveryDate = models.DateTimeField(blank=True, null=True)
    shipByDate = models.DateTimeField(blank=True, null=True)
    # This field is reserved for internal or future use
    sourceTimeZone = models.CharField(max_length=30, blank=True, null=True)


class LineItemProperties(models.Model):
    line_item = models.OneToOneField(
        EbayOrderLineItem, on_delete=models.CASCADE, related_name="properties"
    )
    # Fields
    buyerProtection = models.BooleanField()
    fromBestOffer = models.BooleanField(blank=True, null=True)
    soldViaAdCampaign = models.BooleanField(blank=True, null=True)


class LineItemRefund(models.Model):
    line_item = models.ForeignKey(
        EbayOrderLineItem,
        on_delete=models.CASCADE,
        related_name="refunds",
        related_query_name="refund",
    )
    # Fields
    refundDate = models.DateTimeField(blank=True, null=True)
    # This field is reserved for internal or future use
    refundId = models.CharField(max_length=255, blank=True, null=True)
    refundReferenceId = models.CharField(max_length=100, blank=True, null=True)


class LineItemRefundAmount(AbstractAmount):
    line_item_refund = models.OneToOneField(
        LineItemRefund, on_delete=models.CASCADE, related_name="amount"
    )


class LineItemTax(models.Model):
    line_item = models.ForeignKey(
        EbayOrderLineItem,
        on_delete=models.CASCADE,
        related_name="taxes",
        related_query_name="tax",
    )


class LineItemTaxAmount(AbstractAmount):
    tax = models.OneToOneField(
        LineItemTax, on_delete=models.CASCADE, related_name="amount"
    )


class LineItemTotal(AbstractAmount):
    line_item = models.OneToOneField(
        EbayOrderLineItem, on_delete=models.CASCADE, related_name="total"
    )
