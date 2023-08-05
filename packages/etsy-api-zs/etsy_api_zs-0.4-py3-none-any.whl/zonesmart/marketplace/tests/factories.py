from factory import DjangoModelFactory, SubFactory

from zonesmart.marketplace.models import (
    Channel,
    Domain,
    Marketplace,
    MarketplaceUserAccount,
)
from zonesmart.users.tests.factories import AdminFactory


class MarketplaceFactory(DjangoModelFactory):
    name = "Test marketplace"
    unique_name = "test"

    class Meta:
        model = Marketplace
        django_get_or_create = ["unique_name"]


class DomainFactory(DjangoModelFactory):
    name = "Test domain"
    code = "test"
    marketplace = SubFactory(MarketplaceFactory)

    class Meta:
        model = Domain
        django_get_or_create = ["code"]


class MarketplaceUserAccountFactory(DjangoModelFactory):
    user = SubFactory(AdminFactory)
    marketplace = SubFactory(MarketplaceFactory)

    class Meta:
        model = MarketplaceUserAccount


class ChannelFactory(DjangoModelFactory):
    name = "Test available channel"
    marketplace_user_account = SubFactory(MarketplaceUserAccountFactory)
    domain = SubFactory(DomainFactory)

    class Meta:
        model = Channel
        django_get_or_create = ["marketplace_user_account", "domain"]
