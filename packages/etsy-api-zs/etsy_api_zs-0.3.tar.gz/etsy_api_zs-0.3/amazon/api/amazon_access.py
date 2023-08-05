from django.conf import settings

from zonesmart.marketplace.api.marketplace_access import MarketplaceAPIAccess


class AmazonAPIAccess(MarketplaceAPIAccess):
    marketplace_name = "Amazon"

    @property
    def credentials(self):
        conf = settings.AMAZON_APP_CONFIG
        if conf.get("developer_id", False):
            conf.pop("developer_id")
        return conf

    def get_auth_url(self):
        return "https://sellercentral.amazon.com/sellingpartner/developerconsole"
