from amazon.account.models import AmazonUserAccount
from amazon.tests.factories import AmazonMarketplaceUserAccountFactory
from factory import SubFactory
from factory.django import DjangoModelFactory


class AmazonUserAccountFactory(DjangoModelFactory):
    marketplace_user_account = SubFactory(AmazonMarketplaceUserAccountFactory)
    access_token = "amzn.mws.2cb2bde5-d9e4-66b0-1ccf-f1c9adb33002"

    class Meta:
        model = AmazonUserAccount
        django_get_or_create = ["marketplace_user_account"]
