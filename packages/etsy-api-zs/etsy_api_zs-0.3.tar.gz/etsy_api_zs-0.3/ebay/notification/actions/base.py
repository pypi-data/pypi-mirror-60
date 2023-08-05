from datetime import datetime

from ebay.api.ebay_trading_api_action import EbayTradingAPIAction
from ebay.data import enums


class RemoteGetEbayNotificationSettings(EbayTradingAPIAction):
    """
    Docs:
    https://developer.ebay.com/Devzone/XML/docs/Reference/eBay/GetNotificationPreferences.html
    """

    verb = "GetNotificationPreferences"

    def get_params(self, preference_level: str = "Application", **kwargs):
        assert preference_level in [
            "Application",
            "Event",
            "User",
            "UserData",
        ], f'Недопустимое значение "preference_level": {preference_level}'
        return {
            "PreferenceLevel": preference_level,
            "OutputSelector": None,
        }

    def make_request(self, **kwargs):
        is_success, message, objects = super().make_request(**kwargs)
        if objects.get("errors", []):
            if objects["errors"][0].get("ErrorCode", None) == "12209":
                is_success = True
                objects["results"] = []
        return is_success, message, objects


class RemoteGetEbayNotificationsUsage(EbayTradingAPIAction):
    """
    Docs:
    https://developer.ebay.com/Devzone/XML/docs/Reference/eBay/GetNotificationsUsage.html
    FIX: timeout problem
    """

    verb = "GetNotificationsUsage"

    def get_params(
        self,
        listingId: str = None,
        start_time: str = None,
        end_time: str = None,
        **kwargs,
    ):
        if not end_time:
            end_time = datetime.now().isoformat()

        return {
            "ItemID": listingId,
            "StartTime": start_time,
            "EndTime": end_time,
        }


class SetEbayNotificationSettings(EbayTradingAPIAction):
    """
    Docs:
    https://developer.ebay.com/Devzone/XML/docs/Reference/eBay/SetNotificationPreferences.html
    """

    verb = "SetNotificationPreferences"

    def get_params(
        self,
        alert_enable: bool = True,
        app_enable: bool = True,
        alert_email: str = None,
        app_url: str = None,
        device_type: str = "Platform",
        delivery_url_name_list: list = None,
        delivery_details: list = None,
        subscriptions: list = None,
        **kwargs,
    ):
        assert device_type in [
            "Platform",
            "ClientsAlert",
        ], f'Недопустимое значение "DeviceType": {device_type}'

        return {
            "ApplicationDeliveryPreferences": {
                "AlertEmail": alert_email,
                "AlertEnable": "Enable" if alert_enable else "Disable",
                "ApplicationEnable": "Enable" if app_enable else "Disable",
                "ApplicationURL": app_url,
                "DeliveryURLDetails": delivery_details,
                "DeviceType": device_type,
            },
            "DeliveryURLName": ",".join(delivery_url_name_list)
            if delivery_url_name_list
            else None,
            "UserDeliveryPreferenceArray": subscriptions,
        }


class EnableEbayNotifications(SetEbayNotificationSettings):
    def get_params(self, **kwargs):
        kwargs = {"app_enable": "Enable"}
        return super().get_params(**kwargs)


class DisableEbayNotifications(SetEbayNotificationSettings):
    def get_params(self, **kwargs):
        kwargs = {"app_enable": "Disable"}
        return super().get_params(**kwargs)


class SetEbayNotificationsURL(SetEbayNotificationSettings):
    def get_params(self, app_url: str, **kwargs):
        kwargs = {"app_url": app_url}
        return super().get_params(**kwargs)


class ReviseEbayNotifications(SetEbayNotificationSettings):
    def get_params(self, notifications: list, enable: bool, **kwargs):
        for notification in notifications:
            assert (
                notification in enums.NotificationEventTypeEnum
            ), f'Недопустимое значение "notification": {notification}'

        kwargs["subscriptions"] = [
            {
                "NotificationEnable": [
                    {
                        "EventType": notification,
                        "EventEnable": "Enable" if enable else "Disable",
                    }
                    for notification in notifications
                ]
            }
        ]
        return super().get_params(**kwargs)


class SubscribeEbayNotification(ReviseEbayNotifications):
    def get_params(self, **kwargs):
        kwargs["enable"] = True
        return super().get_params(**kwargs)


class UnsubscribeEbayNotification(ReviseEbayNotifications):
    def get_params(self, **kwargs):
        kwargs["enable"] = False
        return super().get_params(**kwargs)
