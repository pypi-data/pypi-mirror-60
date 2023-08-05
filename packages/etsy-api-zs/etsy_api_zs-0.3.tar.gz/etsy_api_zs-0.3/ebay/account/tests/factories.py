from ebay.account.models import EbayUserAccount
from ebay.tests.factories import EbayMarketplaceUserAccountFactory
from factory import SubFactory
from factory.django import DjangoModelFactory


class EbayUserAccountFactory(DjangoModelFactory):
    marketplace_user_account = SubFactory(EbayMarketplaceUserAccountFactory)
    refresh_token = "v^1.1#i^1#p^3#f^0#r^1#I^3#t^Ul4xMF83OkREMTIxMzU4MTJGODcwN0QyQTdEOTk3RDcyREIzQTlFXzNfMSNFXjI2MA=="
    refresh_token_expiry = "2021-10-10T08:00:00Z"
    sandbox = False

    class Meta:
        model = EbayUserAccount
        django_get_or_create = ["marketplace_user_account"]


class EbaySandboxUserAccountFactory(EbayUserAccountFactory):
    refresh_token = "v^1.1#i^1#I^3#f^0#r^1#p^3#t^Ul4xMF8yOjVFNzUzMUUyNDY1MjFFMzA3OUQzRjY4NDU1RjhCNzJCXzNfMSNFXjEyODQ="
    sandbox = True
