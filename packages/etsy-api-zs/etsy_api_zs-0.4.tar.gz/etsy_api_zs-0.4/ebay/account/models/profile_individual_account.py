from django.db import models

from ebay.account.models import AbstractContact, AbstractPhone, EbayUserAccountProfile
from ebay.models import AbstractAddress

from zonesmart.data.enums import AllCountryCodeEnum
from zonesmart.models import NestedUpdateOrCreateModelManager


class IndividualAccount(AbstractContact):
    profile = models.OneToOneField(
        EbayUserAccountProfile,
        on_delete=models.CASCADE,
        related_name="individualAccount",
    )
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")

    objects = NestedUpdateOrCreateModelManager()

    class Meta:
        verbose_name = "Индивидуальный аккаунт"
        verbose_name_plural = "Индивидуальные аккаунты"


class IndividualPrimaryPhone(AbstractPhone):
    individual_account = models.OneToOneField(
        IndividualAccount, on_delete=models.CASCADE, related_name="primaryPhone"
    )

    class Meta:
        verbose_name = "Основной телефон"
        verbose_name_plural = "Основные телефоны"


class IndividualRegistrationAddress(AbstractAddress):
    individual_account = models.OneToOneField(
        IndividualAccount, on_delete=models.CASCADE, related_name="registrationAddress"
    )
    countryCode = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        choices=AllCountryCodeEnum,
        verbose_name="Страна",
    )

    class Meta:
        verbose_name = "Адресс регистрации"
        verbose_name_plural = "Адреса регистрации"


class IndividualSecondaryPhone(AbstractPhone):
    individual_account = models.OneToOneField(
        IndividualAccount, on_delete=models.CASCADE, related_name="secondaryPhone"
    )

    class Meta:
        verbose_name = "Дополнительный телефон"
        verbose_name_plural = "Дополнительные телефоны"
