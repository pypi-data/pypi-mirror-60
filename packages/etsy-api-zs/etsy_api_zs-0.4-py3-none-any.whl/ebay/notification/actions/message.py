from ebay.notification.actions.base import ReviseEbayNotifications


class ReviseEbayMessageNotifications(ReviseEbayNotifications):
    def get_params(self, **kwargs):
        kwargs["notifications"] = [
            "MyMessagesM2MMessageHeader",
            "MyMessageseBayMessageHeader",
        ]
        return super().get_params(**kwargs)


class SubscribeEbayMessageNotifications(ReviseEbayMessageNotifications):
    def get_params(self, **kwargs):
        kwargs["enable"] = True
        return super().get_params(**kwargs)


class UnsubscribeEbayMessageNotifications(ReviseEbayMessageNotifications):
    def get_params(self, **kwargs):
        kwargs["enable"] = False
        return super().get_params(**kwargs)
