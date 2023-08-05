from typing import Tuple

from ebay.order.models import (
    EbayOrder,
    HoldAmount,
    OrderRefund,
    OrderRefundAmount,
    Payment,
    PaymentAmount,
    PaymentHold,
    PaymentSummary,
    SellerActionsToRelease,
    TotalDueSeller,
)


def update_or_create_payment_summary(
    order: EbayOrder, data: dict
) -> Tuple[PaymentSummary, bool]:
    payment_data_list = data.pop("payments", None)
    order_refund_data_list = data.pop("refunds", None)
    total_due_seller_data = data.pop("total_due_seller", None)
    instance: PaymentSummary
    created: bool
    instance, created = PaymentSummary.objects.update_or_create(
        order=order, defaults=data
    )
    # Payment
    if payment_data_list:
        for payment_data in payment_data_list:
            update_or_create_payment(payment_summary=instance, data=payment_data)
    # OrderRefund
    if order_refund_data_list:
        for order_refund_data in order_refund_data_list:
            update_or_create_order_refund(
                payment_summary=instance, data=order_refund_data
            )
    # TotalDueSeller
    if total_due_seller_data:
        update_or_create_total_due_seller(
            payment_summary=instance, data=total_due_seller_data
        )
    return instance, created


def update_or_create_payment(
    payment_summary: PaymentSummary, data: dict
) -> Tuple[Payment, bool]:
    amount_data = data.pop("amount")
    payment_hold_data_list = data.pop("payment_holds", None)
    instance: Payment
    created: bool
    instance, created = Payment.objects.update_or_create(
        payment_summary=payment_summary, defaults=data
    )
    # PaymentAmount
    if amount_data:
        update_or_create_payment_amount(payment=instance, data=amount_data)
    # PaymentHold
    if payment_hold_data_list:
        for payment_hold_data in payment_hold_data_list:
            update_or_create_payment_hold(payment=instance, data=payment_hold_data)
    return instance, created


def update_or_create_payment_amount(
    payment: Payment, data: dict
) -> Tuple[PaymentAmount, bool]:
    instance: PaymentAmount
    created: bool
    instance, created = PaymentAmount.objects.update_or_create(
        payment=payment, defaults=data
    )
    return instance, created


def update_or_create_payment_hold(
    payment: Payment, data: dict
) -> Tuple[PaymentHold, bool]:
    amount_data = data.pop("amount", None)
    seller_action_to_release_data_list = data.pop("seller_actions_to_release", None)
    instance: PaymentHold
    created: bool
    instance, created = PaymentHold.objects.update_or_create(
        payment=payment, defaults=data
    )
    # HoldAmount
    if amount_data:
        update_or_create_hold_amount(payment_hold=instance, data=amount_data)
    # SellerActionsToRelease
    if seller_action_to_release_data_list:
        for seller_action_to_release_data in seller_action_to_release_data_list:
            update_or_create_seller_action_to_release(
                payment_hold=instance, data=seller_action_to_release_data
            )
    return instance, created


def update_or_create_hold_amount(
    payment_hold: PaymentHold, data: dict
) -> Tuple[HoldAmount, bool]:
    instance: HoldAmount
    created: bool
    instance, created = HoldAmount.objects.update_or_create(
        payment_hold=payment_hold, defaults=data
    )
    return instance, created


def update_or_create_seller_action_to_release(
    payment_hold: PaymentHold, data: dict
) -> Tuple[SellerActionsToRelease, bool]:
    instance: SellerActionsToRelease
    created: bool
    instance, created = SellerActionsToRelease.objects.update_or_create(
        payment_hold=payment_hold, defaults=data
    )
    return instance, created


def update_or_create_order_refund(
    payment_summary: PaymentSummary, data: dict
) -> Tuple[OrderRefund, bool]:
    amount_data = data.pop("amount")
    instance: OrderRefund
    created: bool
    instance, created = OrderRefund.objects.update_or_create(
        payment_summary=payment_summary, defaults=data
    )
    # OrderRefundAmount
    if amount_data:
        update_or_create_order_refund_amount(order_refund=instance, data=amount_data)
    return instance, created


def update_or_create_order_refund_amount(
    order_refund: OrderRefund, data: dict
) -> Tuple[OrderRefundAmount, bool]:
    instance: OrderRefundAmount
    created: bool
    instance, created = OrderRefundAmount.objects.update_or_create(
        order_refund=order_refund, defaults=data
    )
    return instance, created


def update_or_create_total_due_seller(
    payment_summary: PaymentSummary, data: dict
) -> Tuple[TotalDueSeller, bool]:
    instance: TotalDueSeller
    created: bool
    instance, created = TotalDueSeller.objects.update_or_create(
        payment_summary=payment_summary, defaults=data
    )
    return instance, created
