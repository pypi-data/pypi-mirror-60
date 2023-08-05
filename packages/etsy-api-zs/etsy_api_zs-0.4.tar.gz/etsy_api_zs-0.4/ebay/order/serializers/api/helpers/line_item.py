from typing import Tuple

from ebay.order.models import (
    AppliedPromotion,
    DiscountAmount,
    DiscountedLineItemCost,
    EbayOrder,
    EbayOrderLineItem,
    ImportCharges,
    LineItemCost,
    LineItemDeliveryCost,
    LineItemFulfillmentInstructions,
    LineItemProperties,
    LineItemRefund,
    LineItemRefundAmount,
    LineItemTax,
    LineItemTaxAmount,
    LineItemTotal,
    ShippingCost,
    ShippingIntermediationFee,
)


def update_or_create_line_item(
    order: EbayOrder, data: dict
) -> Tuple[EbayOrderLineItem, bool]:
    applied_promotion_data_list = data.pop("applied_promotions")
    delivery_cost_data = data.pop("delivery_cost")
    discounted_line_item_cost_data = data.pop("discounted_line_item_cost", None)
    line_item_cost_data = data.pop("line_item_cost")
    line_item_fulfillment_instructions_data = data.pop(
        "line_item_fulfillment_instructions"
    )
    properties_data = data.pop("properties")
    line_item_refunds_data_list = data.pop("refunds", None)
    taxes_data_list = data.pop("taxes")
    total_data = data.pop("total")
    instance: EbayOrderLineItem
    created: bool
    instance, created = EbayOrderLineItem.objects.update_or_create(
        order=order, defaults=data
    )
    # AppliedPromotion
    for applied_promotion_data in applied_promotion_data_list:
        update_or_create_applied_promotion(
            line_item=instance, data=applied_promotion_data
        )
    # LineItemDeliveryCost
    if delivery_cost_data:
        update_or_create_line_item_delivery_cost(
            line_item=instance, data=delivery_cost_data
        )
    # DiscountedLineItemCost
    if discounted_line_item_cost_data:
        update_or_create_discounted_line_item_cost(
            line_item=instance, data=discounted_line_item_cost_data
        )
    # LineItemCost
    if line_item_cost_data:
        update_or_create_line_item_cost(line_item=instance, data=line_item_cost_data)
    # LineItemFulfillmentInstructions
    if line_item_fulfillment_instructions_data:
        update_or_create_line_item_fulfillment_instructions(
            line_item=instance, data=line_item_fulfillment_instructions_data
        )
    # LineItemProperties
    if properties_data:
        update_or_create_line_item_properties(line_item=instance, data=properties_data)
    # LineItemRefund
    if line_item_refunds_data_list:
        for line_item_refunds_data in line_item_refunds_data_list:
            update_or_create_line_item_refund(
                line_item=instance, data=line_item_refunds_data
            )
    # LineItemTax
    if taxes_data_list:
        for tax_data in taxes_data_list:
            update_or_create_line_item_tax(line_item=instance, data=tax_data)
    # LineItemTotal
    if total_data:
        update_or_create_line_item_total(line_item=instance, data=total_data)
    return instance, created


def update_or_create_applied_promotion(
    line_item: EbayOrderLineItem, data: dict
) -> Tuple[AppliedPromotion, bool]:
    discount_amount = data.pop("discount_amount", None)
    instance: AppliedPromotion
    created: bool
    instance, created = AppliedPromotion.objects.update_or_create(
        line_item=line_item, defaults=data
    )
    # DiscountAmount
    if discount_amount:
        update_or_create_discount_amount(applied_promotion=instance, data=data)
    return instance, created


def update_or_create_discount_amount(
    applied_promotion: AppliedPromotion, data: dict
) -> Tuple[DiscountAmount, bool]:
    instance: DiscountAmount
    created: bool
    instance, created = DiscountAmount.objects.update_or_create(
        applied_promotion=applied_promotion, defaults=data
    )
    return instance, created


def update_or_create_line_item_delivery_cost(
    line_item: EbayOrderLineItem, data: dict
) -> Tuple[LineItemDeliveryCost, bool]:
    import_charges_data = data.pop("import_charges", None)
    shipping_cost_data = data.pop("shipping_cost", None)
    shipping_intermediation_fee_data = data.pop("shipping_intermediation_fee", None)
    instance: LineItemDeliveryCost
    created: bool
    instance, created = LineItemDeliveryCost.objects.update_or_create(
        line_item=line_item, defaults=data
    )
    # ImportCharges
    if import_charges_data:
        update_or_create_import_charges(
            delivery_cost=instance, data=import_charges_data
        )
    # ShippingCost
    if shipping_cost_data:
        update_or_create_shipping_cost(delivery_cost=instance, data=shipping_cost_data)
    # ShippingIntermediationFee
    if shipping_intermediation_fee_data:
        update_or_create_shipping_intermediation_fee(
            delivery_cost=instance, data=shipping_intermediation_fee_data
        )
    return instance, created


def update_or_create_import_charges(
    delivery_cost: LineItemDeliveryCost, data: dict
) -> Tuple[ImportCharges, bool]:
    instance: ImportCharges
    created: bool
    instance, created = ImportCharges.objects.update_or_create(
        delivery_cost=delivery_cost, defaults=data
    )
    return instance, created


def update_or_create_shipping_cost(
    delivery_cost: LineItemDeliveryCost, data: dict
) -> Tuple[ShippingCost, bool]:
    instance: ShippingCost
    created: bool
    instance, created = ShippingCost.objects.update_or_create(
        delivery_cost=delivery_cost, defaults=data
    )
    return instance, created


def update_or_create_shipping_intermediation_fee(
    delivery_cost: LineItemDeliveryCost, data: dict
) -> Tuple[ShippingIntermediationFee, bool]:
    instance: ShippingIntermediationFee
    created: bool
    instance, created = ShippingIntermediationFee.objects.update_or_create(
        delivery_cost=delivery_cost, defaults=data
    )
    return instance, created


def update_or_create_discounted_line_item_cost(
    line_item: EbayOrderLineItem, data: dict
) -> Tuple[DiscountedLineItemCost, bool]:
    instance: DiscountedLineItemCost
    created: bool
    instance, created = DiscountedLineItemCost.objects.update_or_create(
        line_item=line_item, defaults=data
    )
    return instance, created


def update_or_create_line_item_cost(
    line_item: EbayOrderLineItem, data: dict
) -> Tuple[LineItemCost, bool]:
    instance: LineItemCost
    created: bool
    instance, created = LineItemCost.objects.update_or_create(
        line_item=line_item, defaults=data
    )
    return instance, created


def update_or_create_line_item_fulfillment_instructions(
    line_item: EbayOrderLineItem, data: dict
) -> Tuple[LineItemFulfillmentInstructions, bool]:
    instance: LineItemFulfillmentInstructions
    created: bool
    instance, created = LineItemFulfillmentInstructions.objects.update_or_create(
        line_item=line_item, defaults=data
    )
    return instance, created


def update_or_create_line_item_properties(
    line_item: EbayOrderLineItem, data: dict
) -> Tuple[LineItemProperties, bool]:
    instance: LineItemProperties
    created: bool
    instance, created = LineItemProperties.objects.update_or_create(
        line_item=line_item, defaults=data
    )
    return instance, created


def update_or_create_line_item_refund(
    line_item: EbayOrderLineItem, data: dict
) -> Tuple[LineItemRefund, bool]:
    amount_data = data.pop("amount", None)
    instance: LineItemRefund
    created: bool
    instance, created = LineItemRefund.objects.update_or_create(
        line_item=line_item, defaults=data
    )
    if amount_data:
        update_or_create_line_item_refund_amount(
            line_item_refund=instance, data=amount_data
        )
    return instance, created


def update_or_create_line_item_refund_amount(
    line_item_refund: LineItemRefund, data: dict
) -> Tuple[LineItemRefundAmount, bool]:
    instance: LineItemRefundAmount
    created: bool
    instance, created = LineItemRefundAmount.objects.update_or_create(
        line_item_refund=line_item_refund, defaults=data
    )
    return instance, created


def update_or_create_line_item_tax(
    line_item: EbayOrderLineItem, data: dict
) -> Tuple[LineItemTax, bool]:
    amount_data = data.pop("amount", None)
    instance: LineItemTax
    created: bool
    instance, created = LineItemTax.objects.update_or_create(
        line_item=line_item, defaults=data
    )
    # LineItemTaxAmount
    if amount_data:
        update_or_create_line_item_tax_amount(tax=instance, data=amount_data)
    return instance, created


def update_or_create_line_item_tax_amount(
    tax: LineItemTax, data: dict
) -> Tuple[LineItemTaxAmount, bool]:
    instance: LineItemTaxAmount
    created: bool
    instance, created = LineItemTaxAmount.objects.update_or_create(
        tax=tax, defaults=data
    )
    return instance, created


def update_or_create_line_item_total(
    line_item: EbayOrderLineItem, data: dict
) -> Tuple[LineItemTotal, bool]:
    instance: LineItemTotal
    created: bool
    instance, created = LineItemTotal.objects.update_or_create(
        line_item=line_item, defaults=data
    )
    return instance, created
