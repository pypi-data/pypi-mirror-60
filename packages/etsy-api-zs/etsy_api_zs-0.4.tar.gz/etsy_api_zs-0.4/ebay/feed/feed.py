# import csv
# import os

# from django.core.exceptions import ObjectDoesNotExist

# from ebay.feed import resources
# from ebay.policy import models as policy_models
# from ebay.product import models as ebay_models

# from zonesmart.marketplace.models import Domain
# from zonesmart.product import models as base_models
# from zonesmart.utils.logger import get_logger

# logger = get_logger(app_name=__file__)


# class ProductFeedError(Exception):
#     pass


# class ProductFeed:

#     attr_to_column = {
#         'name': 'Title',
#         'description': 'Product Description',
#         'main_image': 'Picture URL 1',
#         'condition': 'Condition',
#         'conditionDescription': 'Condition Description',
#         'packageType': 'Package Type',
#         'localized_for': 'Localized For',
#         'price': 'List Price',
#         'quantity': 'Total Ship To Home Quantity',
#         'category': 'Category',
#         'fulfillmentPolicy': 'Shipping Policy',
#         'paymentPolicy': 'Payment Policy',
#         'returnPolicy': 'Return Policy',
#         'quantityLimitPerBuyer': 'Max Quantity Per Buyer',
#         'domain': 'Channel ID',
#         'sku': 'SKU',
#         'mpn': 'MPN',
#         'epid': 'ePID',
#         'brand': 'Brand',
#         # 'manufacturer': '',
#         'localizedFor': 'Localized For',
#     }

#     ebay_fields = [
#         'name',
#         'description',
#         'main_image',
#         'condition',
#         'conditionDescription',
#         'packageType',
#         'localizedFor',
#         'price',
#         'quantity',
#         'category',
#         'fulfillmentPolicy',
#         'paymentPolicy',
#         'returnPolicy',
#         'quantityLimitPerBuyer',
#         'domain',
#     ]
#     ebay_special_fields = [
#         'price',
#         'category',
#         'fulfillmentPolicy',
#         'paymentPolicy',
#         'returnPolicy',
#         'domain',
#         'main_image',
#         'epid',
#     ]
#     base_fields = [
#         'sku',
#         'name',
#         'description',
#         'main_image',
#         'mpn',
#         'brand',
#         # 'manufacturer': '',
#         'price',
#         'quantity',
#     ]
#     base_special_fields = ['price', 'main_image']
#     required_fields = ['sku', 'name', 'description', 'main_image']

#     def create_base_product(self, row, user):
#         kwargs = {
#             field: row[self.attr_to_column[field]]
#             for field in self.base_fields
#             if field not in self.base_special_fields and self.attr_to_column[field] in row
#         }
#         try:
#             base_product = base_models.Product.objects.get(user=user, sku=row[self.attr_to_column['sku']])
#         except ObjectDoesNotExist:
#             base_product = base_models.Product.objects.create(**kwargs)
#             created = True
#         else:
#             base_models.Product.objects.filter(id=base_product.id).update(**kwargs)
#             created = False
#         # создание особых полей
#         for field in self.base_special_fields:
#             method = getattr(self, f'import_base_{field}', None)
#             if method and (self.attr_to_column[field] in row):
#                 base_product = method(base_product, row[self.attr_to_column[field]])
#         logger.debug(f"Базовый товар успешно {'создан' if created else 'обновлён'}: {base_product.__dict__}")
#         return base_product

#     def create_ebay_product(self, row, base_product):
#         kwargs = {
#             field: row[self.attr_to_column[field]]
#             for field in self.ebay_fields
#             if field not in self.ebay_special_fields and self.attr_to_column[field] in row
#         }
#         try:
#             ebay_product = ebay_models.EbayProduct.objects.get(product=base_product)
#         except ObjectDoesNotExist:
#             ebay_product = ebay_models.EbayProduct.objects.create(
#                 product=base_product,
#                 **kwargs,
#             )
#             created = True
#         else:
#             ebay_models.EbayProduct.objects.filter(id=ebay_product.id).update(**kwargs)
#             created = False
#         # создание особых полей
#         for field in self.ebay_special_fields:
#             method = getattr(self, f'import_ebay_{field}', None)
#             if method and (self.attr_to_column[field] in row):
#                 ebay_product = method(ebay_product, row[self.attr_to_column[field]])
#         logger.debug(f"Товар eBay успешно {'создан' if created else 'обновлён'}: {ebay_product.__dict__}")
#         return ebay_product

#     def create_aspects(self, row, ebay_product):
#         num = 0
#         for i in range(1, 26):
#             try:
#                 name = row[f'Attribute Name {i}']
#                 value = row[f'Attribute Value {i}']
#             except KeyError:
#                 continue
#             if name and value:
#                 aspect, created = ebay_models.EbayProductAspect.objects.update_or_create(
#                     product=ebay_product,
#                     name=name,
#                     value=value,
#                 )
#                 logger.debug(f"Аспект товара eBay {'создан' if created else 'обновлён'}: {aspect.__dict__}")
#                 num += 1
#         return num

#     def create_extra_images(self, row, ebay_product, base_product):
#         num = 0
#         for i in range(2, 13):
#             try:
#                 url = row[f'Picture URL {i}']
#             except KeyError:
#                 continue
#             if url:
#                 # добавление дополнительной фотографии для товара eBay
#                 ebay_product_extra_image, created = base_models.MarketplaceProductExtraImage.objects.get_or_create(
#                     marketplace_product=ebay_product)
#                 if created or not ebay_product_extra_image.image:
#                     product_image = base_models.ProductImage.objects.create()
#                     ebay_product_extra_image.image = product_image
#                 else:
#                     product_image = ebay_product_extra_image.image
#                 # добавление дополнительной фотографии для базового товара
#                 base_product_extra_image, created = base_models.ProductExtraImage.objects.get_or_create(
#                     product=base_product)
#                 base_product_extra_image.image = product_image
#                 # загрузка файла изображения по url
#                 is_success = product_image.save_file_by_url(url)
#                 if is_success:
#                     logger.debug(f'Дополнительное изображение успешно добавлено (url: {url})')
#                     num += 1
#                 else:
#                     logger.warning(f'Не удалось добавить дополнительное изображение (url: {url})')
#         return num

#     def import_base_main_image(self, base_product, url):
#         product_image = base_models.ProductImage.objects.create()
#         is_success = product_image.save_file_by_url(url)
#         if is_success:
#             base_product.main_image = product_image
#             logger.debug(f'Главное изображение успешно добавлено (url: {url})')
#         else:
#             raise ProductFeedError(f'Не удалось добавить главное изображение (url: {url})')
#         return base_product

#     def import_ebay_main_image(self, ebay_product, url):
#         product_image = base_models.ProductImage.objects.create()
#         is_success = product_image.save_file_by_url(url)
#         if is_success:
#             ebay_product.main_image = product_image
#             logger.debug(f'Главное изображение успешно добавлено (url: {url})')
#         else:
#             raise ProductFeedError(f'Не удалось добавить главное изображение (url: {url})')
#         return ebay_product

#     def import_ebay_price(self, ebay_product, price_value):
#         price = base_models.ProductPrice.objects.create(currency='USD', value=price_value)
#         ebay_product.price = price
#         # ebay_product.price.currency = 'USD'
#         # ebay_product.price.value = price_value
#         return ebay_product

#     def export_price(self, ebay_product, field, row):
#         row[field] = ebay_product.price.value
#         return row

#     def import_ebay_category(self, ebay_product, category_id):
#         try:
#             category = ebay_models.EbayCategory.objects.get(category_id=category_id)
#         except ObjectDoesNotExist:
#             raise ProductFeedError(f'Категория не существует в базе (id: {category_id})')
#         ebay_product.category = category
#         return ebay_product

#     def export_ebay_category(self, ebay_product, field, row):
#         row[field] = ebay_product.category.id
#         return row

#     def import_ebay_fulfillmentPolicy(self, ebay_product, policy_name):
#         try:
#             policy = policy_models.FulfillmentPolicy.objects.get(name=policy_name)
#         except ObjectDoesNotExist:
#             raise ProductFeedError(f'Политика фулфилмента не существует в базе (name: {policy_name})')
#         ebay_product.fulfillmentPolicy = policy
#         return ebay_product

#     def export_ebay_fulfillmentPolicy(self, ebay_product, field, row):
#         row[field] = ebay_product.fulfillmentPolicy.name
#         return row

#     def import_ebay_paymentPolicy(self, ebay_product, policy_name):
#         try:
#             policy = policy_models.PaymentPolicy.objects.get(name=policy_name)
#         except ObjectDoesNotExist:
#             raise ProductFeedError(f'Политика оплаты не существует в базе (name: {policy_name})')
#         ebay_product.paymentPolicy = policy
#         return ebay_product

#     def export_ebay_paymentPolicy(self, ebay_product, field, row):
#         row[field] = ebay_product.paymentPolicy.name
#         return row

#     def import_ebay_returnPolicy(self, ebay_product, policy_name):
#         try:
#             policy = policy_models.returnPolicy.objects.get(name=policy_name)
#         except ObjectDoesNotExist:
#             raise ProductFeedError(f'Политика возврата не существует в базе (name: {policy_name})')
#         ebay_product.returnPolicy = policy
#         return ebay_product

#     def export_ebay_returnPolicy(self, ebay_product, field, row):
#         row[field] = ebay_product.returnPolicy.name
#         return row

#     def import_ebay_domain(self, ebay_product, domain_code):
#         try:
#             domain = Domain.objects.get(name=domain_code)
#         except ObjectDoesNotExist:
#             raise ProductFeedError(f'Домен не существует в базе ({domain_code})')
#         ebay_product.domain = domain
#         return ebay_product

#     def export_ebay_domain(self, ebay_product, field, row):
#         row[field] = ebay_product.domain.code
#         return row

#     def clean_row(self, row):
#         for key, value in list(row.items()):
#             if not value:
#                 row.pop(key)
#         return row

#     def import_feed(self, file_path, user):
#         with open(file_path, 'r') as file:
#             feed = csv.DictReader(file, delimiter=',')
#             for row in feed:
#                 row = self.clean_row(row)
#                 # проверка наличия обязательных полей
#                 for field in self.required_fields:
#                     column = self.attr_to_column[field]
#                     if (column not in row) or (not row[column]):
#                         raise ProductFeedError(f'Поле "{column}" отсутствует или пусто.')
#                 # создание базового товара
#                 try:
#                     sku = row[self.attr_to_column['sku']]
#                     base_product = base_models.Product.objects.get(user=user, sku=sku)
#                 except ObjectDoesNotExist:
#                     base_product = self.create_base_product(row, user)
#                     logger.debug(f'Создан базовый товар (id: {base_product.id})')
#                 # создание товара eBay
#                 ebay_product = self.create_ebay_product(row, base_product)
#                 logger.debug(f'Создан товар eBay (id: {ebay_product.id})')
#                 # создание аспектов
#                 num = self.create_aspects(row, ebay_product)
#                 logger.debug(f'Добавлены аспекты товара eBay (кол-во: {num})')
#                 # создание дополнительных изображений
#                 num = self.create_extra_images(row, ebay_product, base_product)
#                 logger.debug(f'Добавлены дополнительные изображения товара (num: {num})')
#         logger.info(f'Загрузка завершена (feed: {os.path.basename(file_path)})')

#     def export_feed(self, file_path, user):
#         resource = resources.ProductResource()
#         queryset = ebay_models.EbayProduct.objects.filter(product__user=user)
#         dataset = resource.export(queryset)
#         with open(file_path, 'w') as file:
#             file.write(dataset.csv)
