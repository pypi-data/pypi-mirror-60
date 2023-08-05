from django.contrib import admin

from amazon.product.models import AmazonProduct


@admin.register(AmazonProduct)
class AmazonProductAdmin(admin.ModelAdmin):
    exclude = []


# @admin.register(AmazonAspect)
# class AmazonAspectAdmin(admin.ModelAdmin):
#     exclude = []
#     list_display = ['name', '_aspectValues', 'aspectRequired']
#     list_filter = ['category']


# @admin.register(AmazonProductAspect)
# class AmazonProductAspectAdmin(admin.ModelAdmin):
#     exclude = []
#     list_display = ['name', 'value', '_aspectValues', 'aspectRequired']
#     list_filter = ['category']
