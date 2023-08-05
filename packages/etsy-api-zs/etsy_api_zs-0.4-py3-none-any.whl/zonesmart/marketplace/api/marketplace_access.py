from abc import ABC, abstractmethod

from zonesmart.marketplace.models import Channel, MarketplaceUserAccount
from zonesmart.utils.logger import get_logger

logger = get_logger(app_name=__file__)


class MarketplaceAPIAccess(ABC):
    def __init__(self, instance=None, **kwargs):
        if instance:
            self.channel = instance.channel
            self.marketplace_user_account = instance.marketplace_user_account
            self.account = instance.account
            self.marketplace_id = instance.marketplace_id
        else:
            self.channel = self.set_channel(**kwargs)
            self.marketplace_user_account = self.set_marketplace_user_account(**kwargs)
            self.account = self.set_account(**kwargs)
            self.marketplace_id = self.set_marketplace_id()

    @property
    @abstractmethod
    def marketplace_name(self):
        pass

    @property
    @abstractmethod
    def credentials(self):
        pass

    @property
    @abstractmethod
    def get_auth_url(self):
        pass

    @property
    def app_account_instance(self):
        class _mock:
            access_token = None

        return _mock()

    def set_channel(self, channel=None, channel_id=None, **kwargs):
        if channel_id and channel:
            raise AttributeError("Нельзя одновременно задать channel и channel_id.")
        if channel:
            return channel
        elif channel_id:
            return Channel.objects.get(id=channel_id)

    def set_marketplace_user_account(
        self, marketplace_user_account=None, marketplace_user_account_id=None, **kwargs
    ):
        if marketplace_user_account and marketplace_user_account_id:
            raise AttributeError(
                "Нельзя одновременно задать marketplace_user_account и marketplace_user_account_id."
            )
        if marketplace_user_account:
            return marketplace_user_account
        elif marketplace_user_account_id:
            return MarketplaceUserAccount.objects.get(id=marketplace_user_account_id)
        elif self.channel:
            return self.channel.marketplace_user_account

    def set_account(self, **kwargs):
        if self.marketplace_user_account:
            logger.debug(
                f"Работа с API {self.marketplace_name} на уровне пользователя."
            )
            return self.marketplace_user_account.marketplace_account
        else:
            logger.debug(f"Работа с API {self.marketplace_name} на уровне приложения.")
            return self.app_account_instance

    def set_marketplace_id(self):
        if self.channel:
            return self.channel.domain.code
