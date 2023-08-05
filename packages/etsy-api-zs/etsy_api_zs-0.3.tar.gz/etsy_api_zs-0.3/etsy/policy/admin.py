from django.contrib import admin

import nested_admin
from etsy.policy.models import EtsyShippingTemplate, EtsyShippingTemplateEntry


class EtsyShippingTemplateEntryInline(nested_admin.NestedStackedInline):
    model = EtsyShippingTemplateEntry
    can_delete = False
    extra = 1


@admin.register(EtsyShippingTemplate)
class EtsyShippingTemplateAdmin(nested_admin.NestedModelAdmin):
    inlines = [EtsyShippingTemplateEntryInline]
