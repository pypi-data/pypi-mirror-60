from django.utils import timezone

from ebay.negotiation.models import EbayMessage
from factory import DjangoModelFactory, SubFactory

from zonesmart.marketplace.tests.factories import MarketplaceUserAccountFactory


class EbayMessageFactory(DjangoModelFactory):
    class Meta:
        model = EbayMessage
        django_get_or_create = ["marketplace_user_account"]

    marketplace_user_account = SubFactory(MarketplaceUserAccountFactory)
    message_id = "1"
    folder_id = 1
    sender = "Sender name or nickname"
    subject = "Message subject"
    content = "Message body"
    receive_date = timezone.now()
    expiration_date = timezone.now()
