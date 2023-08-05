from django.db import models

from ebay.data import enums
from multiselectfield import MultiSelectField

from zonesmart.models import UUIDModel


class AbstractRecipientAccountReference(UUIDModel):
    referenceId = models.CharField(max_length=255, blank=True, null=True,)
    referenceType = models.CharField(
        max_length=12,
        choices=enums.RecipientAccountReferenceTypeEnum,
        verbose_name="Reference type",
    )


class AbstractPaymentMethod(UUIDModel):
    brands = MultiSelectField(
        blank=True,
        null=True,
        choices=enums.PaymentInstrumentBrandEnum,
        verbose_name="Brands",
    )
    paymentMethodType = models.CharField(
        max_length=11,
        choices=enums.PaymentMethodTypeEnum,
        verbose_name="Payment method type",
    )
