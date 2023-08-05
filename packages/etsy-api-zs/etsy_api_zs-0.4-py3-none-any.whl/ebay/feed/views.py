# import os
#
# from django.http import HttpResponse, HttpResponseRedirect
# from django.views.generic.base import TemplateView
#
# from ebay.feed import feed
# from ebay.location.models import EbayLocation
# from ebay.product.models import EbayProduct
# from tablib import Dataset
#
# from .resources import LocationResource, LocationResourceError, ProductResource
#
# ext_to_content_type = {
#     'csv': 'text/csv',
#     'json': 'application/json',
#     'xls': 'application/vnd.ms-excel',
# }
#
#
# def export_data(request, filename, resource, queryset=None, ext='csv'):
#     if ext not in ext_to_content_type:
#         raise AttributeError(f'Недопустимое расширение файла ({ext}).')
#     dataset = resource().export(queryset)
#     response = HttpResponse(getattr(dataset, ext), content_type=ext_to_content_type[ext])
#     response['Content-Disposition'] = f'attachment; filename="{filename}.{ext}"'
#     return response
#
#
# def export_location(request):
#     queryset = EbayLocation.objects.filter(user=request.user)
#     return export_data(request, filename='locations', resource=LocationResource, queryset=queryset, ext='csv')
#
#
# def export_product(request):
#     queryset = EbayProduct.objects.filter(product__user=request.user)
#     return export_data(request, filename='products', resource=ProductResource, queryset=queryset, ext='csv')
#
#
# class ImportLocationView(TemplateView):
#
#     template_name = 'ebay/feed/import_location_feed.html'
#
#     def post(self, request, *args, **kwargs):
#         file = request.FILES['feed']
#         file_path = os.path.join(file.name)
#         with open(file_path, 'wb') as local_file:
#             for chunk in file.chunks():
#                 local_file.write(chunk)
#
#         dataset = Dataset()
#         with open(file_path, 'r') as file:
#             dataset.csv = file.read()
#
#         resource = LocationResource()
#         result = resource.import_data(dataset, user=request.user.id, dry_run=False, raise_errors=False)
#         if result.has_errors():
#             raise LocationResourceError('Не удалось загрузить фид складов eBay.')
#         else:
#             resource.import_data(dataset, user=request.user.id, dry_run=False)
#
#         return HttpResponseRedirect('/ebay/location')
#
#
# import_location = ImportLocationView.as_view()
#
#
# class ImportProductView(TemplateView):
#
#     template_name = 'ebay/feed/import_product_feed.html'
#
#     def post(self, request, *args, **kwargs):
#         file = request.FILES['feed']
#         file_path = os.path.join(file.name)
#         with open(file_path, 'wb') as local_file:
#             for chunk in file.chunks():
#                 local_file.write(chunk)
#         feed.ProductFeed().import_feed(file_path, request.user)
#         return HttpResponseRedirect('/ebay/product')
#
#
# import_product = ImportProductView.as_view()
