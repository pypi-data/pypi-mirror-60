from django.db import models

from ebay.data.enums import TimeDurationUnitEnum

from zonesmart.data.enums import AllCountryCodeEnum, CurrencyCodeEnum

# from zonesmart.product.models import AbstractPrice


class AbstractAddress(models.Model):
    addressLine1 = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Первая строка адреса"
    )
    addressLine2 = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Вторая строка адреса"
    )
    city = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Населённый пункт"
    )
    countryCode = models.CharField(
        max_length=2, choices=AllCountryCodeEnum, verbose_name="Страна"
    )
    county = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Округ"
    )
    postalCode = models.CharField(
        max_length=16, blank=True, null=True, verbose_name="Почтовый индекс"
    )
    stateOrProvince = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Штат или провинция"
    )

    class Meta:
        abstract = True

    def __str__(self):
        return ", ".join([self.addressLine1, self.get_countryCode_display()])


class AbstractNonConvertedAmount(models.Model):
    currency = models.CharField(
        max_length=20, choices=CurrencyCodeEnum, verbose_name="Валюта"
    )
    value = models.FloatField(verbose_name="Значение цены")

    def __str__(self):
        return f'{getattr(self, "price", None)} {self.currency}'

    class Meta:
        abstract = True


class AbstractAmount(AbstractNonConvertedAmount):
    convertedFromCurrency = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=CurrencyCodeEnum,
        verbose_name="Валюта исходной цены",
    )
    convertedFromValue = models.FloatField(
        blank=True, null=True, verbose_name="Значение исходной цены"
    )

    def __str__(self):
        return f"{super().__str__()} (исходная цена: {self.convertedFromValue} {self.convertedFromCurrency})"

    class Meta:
        abstract = True


class AbstractDuration(models.Model):
    value = models.PositiveIntegerField(verbose_name="Количество",)
    unit = models.CharField(
        max_length=20,
        choices=TimeDurationUnitEnum,
        verbose_name="Единица измерения времени",
    )

    # class AbstractAmount(AbstractPrice):
    #     # convertedFromCurrency = models.CharField(
    #     #     max_length=20, blank=True, null=True,
    #     #     choices=CurrencyCodeEnum,
    #     #     verbose_name='Валюта исходной цены'
    #     # )
    #     # convertedFromValue = models.FloatField(
    #     #     blank=True, null=True,
    #     #     verbose_name='Значение исходной цены'
    #     # )
    #     # currency = models.CharField(
    #     #     max_length=20, choices=CurrencyCodeEnum,
    #     #     verbose_name='Валюта'
    #     # )
    #     # value = models.FloatField(
    #     #     verbose_name='Значение цены'
    #     # )

    def __str__(self):
        return f"{self.value} {self.unit}"

    class Meta:
        abstract = True
