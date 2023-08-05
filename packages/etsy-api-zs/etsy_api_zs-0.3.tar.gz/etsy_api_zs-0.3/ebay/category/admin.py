from django.contrib import admin

from ebay.category.models import EbayCategory, EbayCategoryTree

from zonesmart.category.admin import (
    MarketplaceCategoryAdmin,
    MarketplaceCategoryTreeAdmin,
)


@admin.register(EbayCategoryTree)
class EbayCategoryTreeAdmin(MarketplaceCategoryTreeAdmin):
    list_display = ["category_tree_id"]


@admin.register(EbayCategory)
class EbayCategoryAdmin(MarketplaceCategoryAdmin):
    list_filter = MarketplaceCategoryAdmin.list_filter + [
        "variationsSupported",
        "transportSupported",
    ]
    list_display = MarketplaceCategoryAdmin.list_display + [
        "variationsSupported",
        "transportSupported",
    ]
