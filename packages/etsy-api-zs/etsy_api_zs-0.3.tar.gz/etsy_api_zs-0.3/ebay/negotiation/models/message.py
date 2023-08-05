from django.db import models

from ebay.data import enums
from ebay.listing.models import EbayListing

from zonesmart.marketplace.models import MarketplaceUserAccount


class EbayMessage(models.Model):
    """
    GetMyMessages: https://developer.ebay.com/Devzone/XML/docs/Reference/eBay/GetMyMessages.html#Output
    GetMemberMessages: https://developer.ebamy.com/Devzone/XML/docs/Reference/eBay/GetMemberMessages.html#Output
    """

    marketplace_user_account = models.ForeignKey(
        MarketplaceUserAccount,
        on_delete=models.CASCADE,
        related_name="ebay_member_messages",
        related_query_name="ebay_member_message",
        verbose_name="Пользовательский аккаунт маркетплейса",
    )
    listing = models.ForeignKey(
        EbayListing,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="messages",
        related_query_name="message",
        verbose_name="Листинг eBay",
    )
    # Fields
    listingId = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="ID листинга"
    )

    message_id = models.CharField(
        max_length=30, primary_key=True, verbose_name="ID сообщения"
    )
    folder_id = models.CharField(max_length=2, verbose_name="ID папки")

    sender = models.CharField(max_length=100, verbose_name="Имя отправителя")
    recipient_id = models.CharField(max_length=30, verbose_name="ID получателя")
    # Null for messages from eBay
    sender_id = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="ID отправителя"
    )
    recipient = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Имя отправителя"
    )

    replied = models.BooleanField(default=False, verbose_name="Отвечено")
    read = models.BooleanField(default=False, verbose_name="Прочитано")
    response_enabled = models.BooleanField(default=False, verbose_name="Ответ возможен")
    response_url = models.URLField(blank=True, null=True, verbose_name="URL для ответа")

    high_priority = models.BooleanField(
        default=False, verbose_name="Высокая приоритетность"
    )
    message_type = models.CharField(
        max_length=50,
        choices=enums.MessageTypeEnum,
        default=enums.MessageTypeEnum.All,
        verbose_name="Тип сообщения",
    )
    subject = models.CharField(max_length=300, verbose_name="Тема сообщения")
    content = models.TextField(verbose_name="Содержимое сообщения")

    receive_date = models.DateTimeField(verbose_name="Дата и время получения сообщения")
    expiration_date = models.DateTimeField(
        verbose_name="Дата и время автоудаления сообщения"
    )

    def __str__(self):
        return (
            f"{self.message_id}: {self.subject} ({self.sender}) ({self.receive_date})"
        )

    class Meta:
        ordering = ["-receive_date"]
