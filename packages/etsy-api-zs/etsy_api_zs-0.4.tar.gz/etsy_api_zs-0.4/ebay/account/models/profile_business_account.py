from django.db import models

from ebay.account.models import AbstractContact, AbstractPhone, EbayUserAccountProfile
from ebay.models import AbstractAddress

from zonesmart.data.enums import AllCountryCodeEnum
from zonesmart.models import NestedUpdateOrCreateModelManager


class BusinessAccount(models.Model):
    profile = models.OneToOneField(
        EbayUserAccountProfile, on_delete=models.CASCADE, related_name="businessAccount"
    )
    # Fields
    doingBusinessAs = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Дополнительное имя, используемое для названия бизнесс аккаунта в системе eBay",
    )
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Имя, используемое для названия бизнесс аккаунта в системе eBay",
    )
    website = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Веб-сайт"
    )

    objects = NestedUpdateOrCreateModelManager()

    class Meta:
        verbose_name = "Информация о бизнесс аккаунте"
        verbose_name_plural = "Информация о бизнесс аккаунтах"


class BusinessAddress(AbstractAddress):
    business_account = models.OneToOneField(
        BusinessAccount, on_delete=models.CASCADE, related_name="address"
    )
    countryCode = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        choices=AllCountryCodeEnum,
        verbose_name="Страна",
    )


class BusinessPrimaryContact(AbstractContact):
    business_account = models.OneToOneField(
        BusinessAccount, on_delete=models.CASCADE, related_name="primaryContact"
    )

    class Meta:
        verbose_name = "Основное контактное лицо"
        verbose_name_plural = "Основные контактные лица"


class BusinessPrimaryPhone(AbstractPhone):
    business_account = models.OneToOneField(
        BusinessAccount, on_delete=models.CASCADE, related_name="primaryPhone"
    )

    class Meta:
        verbose_name = "Основной телефон"
        verbose_name_plural = "Основные телефоны"


class BusinessSecondaryPhone(AbstractPhone):
    business_account = models.OneToOneField(
        BusinessAccount, on_delete=models.CASCADE, related_name="secondaryPhone"
    )

    class Meta:
        verbose_name = "Дополнительный телефон"
        verbose_name_plural = "Дополнительные телефоны"
