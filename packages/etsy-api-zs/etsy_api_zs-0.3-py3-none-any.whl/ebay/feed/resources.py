# from ebay.location.models import EbayLocation
# from ebay.product.models import EbayProduct
# from import_export import resources, widgets
# from import_export.fields import Field

# from zonesmart.marketplace.models import Channel


# class LocationResourceError(Exception):
#     pass


# class LocationResource(resources.ModelResource):
#     channel = Field(attribute='channel', column_name='channel',
#                     widget=widgets.ForeignKeyWidget(Channel))
#     merchantLocationKey = Field(attribute='merchantLocationKey', column_name='Location ID')
#     name = Field(attribute='name', column_name='Name')
#     addressLine1 = Field(attribute='addressLine1', column_name='Address 1')
#     addressLine2 = Field(attribute='addressLine2', column_name='Address 2')
#     city = Field(attribute='city', column_name='City')
#     region = Field(attribute='stateOrProvince', column_name='Region')
#     country = Field(attribute='country', column_name='Country')
#     postalCode = Field(attribute='postalCode', column_name='Postal Code')
#     latitude = Field(attribute='latitude', column_name='Latitude', widget=widgets.DecimalWidget())
#     longitude = Field(attribute='longitude', column_name='Longitude', widget=widgets.DecimalWidget())
#     utc_offset = Field(attribute='utcOffset', column_name='UTC Offset', widget=widgets.CharWidget())
#     phone = Field(attribute='phone', column_name='Phone')
#     locationWebUrl = Field(attribute='locationWebUrl', column_name='url')
#     merchantLocationStatus = Field(attribute='merchantLocationStatus', column_name='Status')
#     fulfillmentCapability = Field(attribute='fulfillmentCapability', column_name='Fulfillment Capability')

#     class Meta:
#         model = EbayLocation
#         import_id_fields = ['merchantLocationKey']
#         fields = []

#     def before_import_row(self, row, **kwargs):
#         Channel = kwargs.get('Channel', None)
#         if Channel is None:
#             raise LocationResourceError('Отсутствует поле Channel!')
#         row['Channel'] = Channel
#         return super().before_import_row(row, **kwargs)

#     def after_export(self, queryset, data, *args, **kwargs):
#         del data['Channel']


# class ProductResourceError(Exception):
#     pass


# class ProductResource(resources.ModelResource):

#     sku = Field(attribute='product__sku', column_name='SKU')
#     name = Field(attribute='product__name', column_name='Title')
#     description = Field(attribute='product__description', column_name='Product Description')
#     main_image = Field(attribute='main_image__image_url', column_name='Picture URL 1')
#     mpn = Field(attribute='product_mpn', column_name='MPN')
#     epid = Field(attribute='epid', column_name='ePID')
#     brand = Field(attribute='product_brand', column_name='Brand')
#     condition = Field(attribute='condition', column_name='Condition')
#     conditionDescription = Field(attribute='conditionDescription', column_name='Condition Description')
#     packageType = Field(attribute='packageType', column_name='Package Type')
#     fulfillmentPolicy = Field(attribute='fulfillmentPolicy__name', column_name='Shipping Policy')
#     paymentPolicy = Field(attribute='paymentPolicy__name', column_name='Payment Policy')
#     returnPolicy = Field(attribute='returnPolicy__name', column_name='Return Policy')
#     price = Field(attribute='price__value', column_name='List Price')
#     quantity = Field(attribute='quantity', column_name='Total Ship To Home Quantity')
#     quantityLimitPerBuyer = Field(attribute='quantityLimitPerBuyer', column_name='Max Quantity Per Buyer')
#     category = Field(attribute='category__category_id', column_name='Category')
#     domain = Field(attribute='domain__name', column_name='Channel ID')
#     localizedFor = Field(attribute='localizedFor', column_name='Localized For')
#     base_special_fields = ['price', 'main_image']
#     required_fields = ['sku', 'name', 'description', 'main_image']

#     class Meta:
#         model = EbayProduct
#         fields = []

#     def import_data(self, *args, **kwargs):
#         raise ProductResourceError('Импорт с помощью данного класса не поддерживается!')

#     def get_export_headers(self):
#         headers = super().get_export_headers()
#         # добавление столбцов для дополнительных изображений товара
#         headers += [f'Picture URL {i}' for i in range(2, 13)]
#         # добавление столбцов для аспектов товара
#         for i in range(1, 26):
#             headers += [f'Attribute Name {i}', f'Attribute Value {i}']
#         return headers

#     def export_resource(self, obj):
#         resource = super().export_resource(obj)
#         # добавление url дополнительных изображений товара
#         extra_images_num = 0
#         if obj.extra_images:
#             extra_images_num = len(obj.extra_images.all())
#             for extra_image in obj.extra_images.all():
#                 resource.append(extra_image.image.image_url if extra_image.image else '')
#         resource += ['' for _ in range(extra_images_num, 11)]
#         # добавление имён и значений аспектов товара
#         aspects_num = 0
#         if obj.aspects:
#             aspects_num = len(obj.aspects.all()) * 2
#             for aspect in obj.aspects.all():
#                 resource += [aspect.name, aspect.value]
#         resource += ['' for _ in range(aspects_num, 50)]
#         return resource

#     def after_export(self, queryset, data, *args, **kwargs):
#         # reorder columns
#         pass
