from django.db import models

from ebay.account.models import EbayUserAccount, EbayAppAccount
from ebay.location.models import EbayLocation
from ebay.models.abstract import AbstractAmount
from ebay.policy.models import FulfillmentPolicy, PaymentPolicy, ReturnPolicy


class EbayUserAccountPrivileges(AbstractAmount):
    ebay_account = models.OneToOneField(
        EbayUserAccount,
        on_delete=models.CASCADE,
        related_name="privileges",
        verbose_name="Пользовательский аккаунт eBay",
    )
    # Fields
    sellerRegistrationCompleted = models.BooleanField(
        blank=True, null=True, verbose_name="Регистрация аккаунта eBay завершена",
    )
    quantity = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name="Ограничение на количество товаров в месяц",
    )

    def __str__(self):
        return f"Ограничения аккаунта eBay ({self.ebay_account})"

    class Meta:
        verbose_name = "Ограничения аккаунта eBay"
        verbose_name_plural = "Ограничения аккаунта eBay"


class EbayUserAccountDefaults(models.Model):
    ebay_account = models.OneToOneField(
        EbayUserAccount,
        on_delete=models.CASCADE,
        related_name="defaults",
        verbose_name="Пользовательский аккаунт eBay",
    )
    # Fields
    location = models.ForeignKey(
        EbayLocation,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Склад по умолчанию",
    )
    fulfillmentPolicy = models.ForeignKey(
        FulfillmentPolicy,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Политика фулфилмента по умолчанию",
    )
    paymentPolicy = models.ForeignKey(
        PaymentPolicy,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Политика оплаты по умолчанию",
    )
    returnPolicy = models.ForeignKey(
        ReturnPolicy,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Политика возврата по умолчанию",
    )

    class Meta:
        verbose_name = "Значения по умолчанию для пользователя eBay"
        verbose_name_plural = "Значения по умолчанию для пользователей eBay"


class EbayAppRateLimits(models.Model):
    ebay_app_account = models.ForeignKey(
        EbayAppAccount, on_delete=models.CASCADE, related_name="rate_limits",
    )
    # Fields
    apiContext = models.CharField(max_length=50, verbose_name="Тип API")
    apiName = models.CharField(max_length=50, verbose_name="Название API")
    apiVersion = models.CharField(
        max_length=10, blank=True, default="", verbose_name="Версия API"
    )

    def __str__(self):
        return f"{self.apiContext} : {self.apiName}"

    class Meta:
        verbose_name = "Ограничение на число запросов"
        verbose_name_plural = "Ограничение на число запросов"


class EbayRateLimitsResource(models.Model):
    rate_limits = models.ForeignKey(
        EbayAppRateLimits, on_delete=models.CASCADE, related_name="resources",
    )
    name = models.CharField(max_length=50, verbose_name="Название ресурса")

    class Meta:
        verbose_name = "Ограничение на число запросов для ресурса"
        verbose_name_plural = "Ограничение на число запросов для ресурса"


class EbayRateLimitsResourceRate(models.Model):
    resource = models.ForeignKey(
        EbayRateLimitsResource, on_delete=models.CASCADE, related_name="rates",
    )
    # Fields
    limit = models.IntegerField(verbose_name="Лимит")
    remaining = models.IntegerField(verbose_name="Остаток")
    reset = models.DateTimeField(verbose_name="Дата и время обновления лимита")
    timeWindow = models.IntegerField(verbose_name="Временное окно")
