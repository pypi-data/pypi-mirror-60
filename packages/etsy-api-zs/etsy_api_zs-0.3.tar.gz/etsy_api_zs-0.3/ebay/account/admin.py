from django.contrib import admin

import nested_admin
from ebay.account import models


@admin.register(models.EbayUserAccount)
class EbayUserAccountAdmin(admin.ModelAdmin):
    verbose_name = "Пользовательский токен для eBay"
    verbose_name_plural = "Пользовательские токены для eBay"
    list_display = ["refresh_token_expiry"]
    readonly_fields = []


@admin.register(models.EbayUserAccountProfile)
class EbayUserAccountProfile(admin.ModelAdmin):
    pass


@admin.register(models.EbayUserAccountPrivileges)
class EbayUserAccountPrivilegesAdmin(admin.ModelAdmin):
    exclude = ["convertedFromCurrency", "convertedFromValue"]


class EbayRateLimitsResourceRateInline(nested_admin.NestedTabularInline):
    model = models.EbayRateLimitsResourceRate
    can_delete = True
    extra = 0


class EbayRateLimitsResourceInline(nested_admin.NestedTabularInline):
    model = models.EbayRateLimitsResource
    can_delete = True
    extra = 0
    inlines = [EbayRateLimitsResourceRateInline]


class EbayAppRateLimitsInline(nested_admin.NestedTabularInline):
    model = models.EbayAppRateLimits
    can_delete = True
    extra = 0
    inlines = [EbayRateLimitsResourceInline]


@admin.register(models.EbayAppAccount)
class EbayAppAccountAdmin(nested_admin.NestedModelAdmin):
    inlines = [EbayAppRateLimitsInline]
