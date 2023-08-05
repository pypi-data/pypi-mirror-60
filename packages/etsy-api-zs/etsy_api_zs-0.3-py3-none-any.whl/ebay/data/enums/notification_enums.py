"""
Docs: https://developer.ebay.com/Devzone/XML/docs/Reference/eBay/types/NotificationEventTypeCodeType.html
"""

ClientAlertsEventTypeEnum = [  # not compatible with PlatformNotifications
    "AccountSummary",
    "AccountSuspended",
    "EmailAddressChanged",
    "PasswordChanged",
    "PaymentDetailChanged",
]

PlatformNotificationEventTypeEnum = [  # not compatible with ClientAlerts
    # BestOffers
    "BestOffer",
    "BestOfferPlaced",
    # Feedbacks
    "Feedback",
    "FeedbackLeft",
    "FeedbackReceived",
    # Listings
    "FixedPriceTransaction",
    "ItemClosed",
    "ItemListed",
    "ItemMarkedPaid",
    "ItemMarkedShipped",
    "ItemOutOfStock",
    "ItemRevised",
    "ItemSold",
    "ItemSuspended",
    # Messages
    "AskSellerQuestion",
    "M2MMessageStatusChange",
    "MyMessageseBayMessage",
    "MyMessageseBayMessageHeader",
    "MyMessagesHighPriorityMessage",
    "MyMessagesM2MMessage",
    "MyMessagesM2MMessageHeader",
    # Orders
    "BuyerResponseDispute",
    "BuyerCancelRequested",
    "OrderInquiryClosed",
    "OrderInquiryEscalatedToCase",
    "OrderInquiryOpened",
    "OrderInquiryProvideShipmentInformation",
    "OrderInquiryReminderForEscalation",
    "ReturnWaitingForSellerInfo",
    # Account
    "TokenRevocation",
    "UserIDChanged",
]

NotificationEventTypeEnum = (
    PlatformNotificationEventTypeEnum  # + ClientAlertsEventTypeEnum
)
