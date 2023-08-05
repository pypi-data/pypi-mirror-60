# import json

from django.db import models

from amazon.category.models import AmazonCategory
from amazon.data import enums

from zonesmart.marketplace.models import Channel

# from zonesmart.models import UUIDModel
from zonesmart.product.models import AbstractMarketplaceProduct, BaseProduct


class AmazonProduct(AbstractMarketplaceProduct):
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        limit_choices_to={
            "domain__marketplace__unique_name__in": [
                "amazon_north_america",
                "amazon_europe",
                "amazon_far_east",
            ],
        },
        related_name="amazon_products",
        related_query_name="amazon_product",
        verbose_name="Пользовательский канал продаж",
    )
    base_product = models.ForeignKey(
        BaseProduct,
        on_delete=models.CASCADE,
        related_name="amazon_products",
        related_query_name="amazon_product",
        verbose_name="Базовый товар",
    )
    REQUIRED_PRODUCT_FIELDS = ["product_id_code", "product_id_code_type"]
    category = models.ForeignKey(
        AmazonCategory,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория товара Amazon",
    )
    condition_type = models.CharField(
        max_length=30,
        choices=enums.Condition.ConditionEnum,
        verbose_name="Состояние товара",
    )
    # Required if condition_type != NEW
    condition_note = models.TextField(
        max_length=1000,
        blank=True,
        default="",
        verbose_name="Описание состояния товара",
    )
    product_tax_code = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        choices=enums.ProductTaxCodeEnum,
        verbose_name="Налоговый код Amazon",
    )
    # Shipping
    merchant_shipping_group_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Название шаблона доставки"
    )
    fulfillment_center_id = models.CharField(
        max_length=30, choices=enums.FulfillmentCenterEnum
    )
    handling_time = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Количество дней, нужное для отправки товара",
    )
    expedited_ship_internationally = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Ускоренная доставка"
    )
    will_ship_internationally = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        choices=enums.WILL_SHIP_INTERNATIONALLY_CHOICES,
        verbose_name="Международная доставка",
    )

    class Meta:
        verbose_name = "Товар Amazon"
        verbose_name_plural = "Товары Amazon"


class AmazonProductBulletPoint(models.Model):
    amazon_product = models.ForeignKey(
        AmazonProduct,
        on_delete=models.CASCADE,
        related_name="bullet_points",
        related_query_name="bullet_point",
        verbose_name="Товар Amazon",
    )
    content = models.TextField(max_length=500, verbose_name="Аспект товара")


class AmazonProductBattery(models.Model):
    amazon_product = models.OneToOneField(
        AmazonProduct,
        on_delete=models.CASCADE,
        related_name="battery_info",
        verbose_name="Товар Amazon",
    )

    batteries_required = models.BooleanField(verbose_name="Требуются батареи")
    # REQ if batteries_required is True
    are_batteries_included = models.BooleanField(
        blank=True, null=True, verbose_name="Содержит батареи"
    )
    # REQ if are_batteries_included is True
    battery_cell_composition = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=enums.BatteryCellCompositionEnum,
        verbose_name="Состав аккумуляторной батареи",
    )
    # REQ if lithium
    battery_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=enums.BatteryTypeEnum,
        verbose_name="Тип батареи",
    )
    # REQ if lithium
    number_of_batteries = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name="Количество батарей"
    )
    # REQ if lithium
    battery_weight = models.FloatField(
        blank=True, null=True, verbose_name="Масса батареи"
    )
    # REQ if battery_weight
    battery_weight_unit_of_measure = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=enums.WeightEnum,
        verbose_name="Единица измерения массы батареи",
    )
    # REQ if lithium
    number_of_lithium_ion_cells = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name="Количество литий-ионных элементов"
    )
    # REQ if lithium
    number_of_lithium_methal_cells = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name="Количество литий-металлических элементов"
    )
    # REQ if lithium
    lithium_battery_packaging = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=enums.LithiumBatteryPackagingEnum,
        verbose_name="Описание упаковки литиевой батареи",
    )
    # REQ if lithium-metal
    lithium_battery_energy_content = models.FloatField(
        blank=True,
        null=True,
        choices=enums.BatteryEnergyContentEnum,
        verbose_name="Ёмкость литиевой батареи (каждой отдельной)",
    )
    # REQ if lithium_battery_energy_content
    lithium_battery_energy_content_unit_of_measure = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Единица ёмкости литиевой батареи",
    )
    # REQ if lithium-ion
    lithium_battery_weight = models.FloatField(
        blank=True, null=True, verbose_name="Масса литиевой батареи"
    )
    # REQ if lithium_battery_weight
    lithium_battery_weight_unit_of_measure = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=enums.WeightEnum,
        verbose_name="Единица измерения массы литиевой батареи",
    )


# class AmazonAspect(UUIDModel):
#     category = models.ForeignKey(AmazonProductCategory, on_delete=models.SET_NULL,
#                                  null=True, verbose_name='Категория товара Amazon')

#     group_name = models.CharField(blank=True, null=True, max_length=255)
#     name = models.CharField(max_length=255)

#     _aspectValues = models.TextField(default='[]')
#     aspectRequired = models.BooleanField()

#     @property
#     def aspectValues(self):
#         return json.loads(self._aspectValues)

#     @aspectValues.setter
#     def aspectValues(self, value):
#         self._aspectValues = json.dumps(self.aspectValues + value)

#     class Meta:
#         verbose_name = 'Непривязанный аспект товара Amazon'
#         verbose_name_plural = 'Непривязанные аспекты товара Amazon'


# class AmazonProductAspect(AmazonAspect):
#     product = models.ForeignKey(AmazonProduct, on_delete=models.CASCADE, null=True,
#                                 related_name='aspects', related_query_name='aspect',
#                                 verbose_name='Товар для Amazon')

#     value = models.CharField(max_length=255, blank=True, null=True)

#     class Meta:
#         verbose_name = 'Аспект товара Amazon'
#         verbose_name_plural = 'Аспекты товара Amazon'
