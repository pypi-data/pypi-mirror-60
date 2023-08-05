from django.contrib import admin


class MarketplaceCategoryTreeAdmin(admin.ModelAdmin):
    exclude = []


class MarketplaceCategoryAdmin(admin.ModelAdmin):
    exclude = []
    list_display = ["name", "name_path", "level", "is_leaf"]
    list_filter = ["category_tree", "level", "is_leaf"]
