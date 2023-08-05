from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
    # Django admin
    path(settings.ADMIN_URL, admin.site.urls),
    # nested_admin
    path("_nested_admin/", include("nested_admin.urls")),
    # Auth urls
    path("api/auth/", include("config.urls.auth")),
    # API urls
    path("api/v1/", include("config.urls.api.v1")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
