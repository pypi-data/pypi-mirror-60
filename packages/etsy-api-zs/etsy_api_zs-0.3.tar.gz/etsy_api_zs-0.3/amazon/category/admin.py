from django.contrib import admin

from amazon.category.models import AmazonCategory, AmazonCategoryTree

from zonesmart.category.admin import (
    MarketplaceCategoryAdmin,
    MarketplaceCategoryTreeAdmin,
)


@admin.register(AmazonCategoryTree)
class AmazonCategoryTreeAdmin(MarketplaceCategoryTreeAdmin):
    pass


@admin.register(AmazonCategory)
class AmazonCategoryAdmin(MarketplaceCategoryAdmin):
    pass
