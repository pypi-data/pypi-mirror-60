from uuid import uuid4

from ebay.location.models import EbayLocation
from ebay.tests.factories import EbayMarketplaceUserAccountFactory
from factory import Faker, LazyAttribute, Sequence, SubFactory, fuzzy
from factory.django import DjangoModelFactory

from zonesmart.data.enums import CountryCodeEnum


class EbayLocationFactory(DjangoModelFactory):
    class Meta:
        model = EbayLocation
        django_get_or_create = ["marketplace_user_account", "merchantLocationKey"]

    name = Sequence(lambda n: f"Test Location {n}")
    marketplace_user_account = SubFactory(EbayMarketplaceUserAccountFactory)
    merchantLocationKey = LazyAttribute(lambda x: str(uuid4()))
    countryCode = fuzzy.FuzzyChoice(choices=CountryCodeEnum, getter=lambda x: x[0],)
    city = Faker("city")
    addressLine1 = Faker("address")
    addressLine2 = Faker("address")
    county = Faker("state")
    stateOrProvince = Faker("state")
    postalCode = Faker("postalcode")
    latitude = Faker("longitude")
    longitude = Faker("latitude")
    utcOffset = fuzzy.FuzzyChoice(
        choices=EbayLocation.utcOffsetChoices, getter=lambda x: x[0],
    )
    locationAdditionalInformation = Faker("sentence")
    locationInstructions = Faker("sentence")
    locationWebUrl = Faker("url")
    phone = Faker("phone_number")
