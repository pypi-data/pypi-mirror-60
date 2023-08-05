from django.urls import path

from zonesmart.users import views

app_name = "zonesmart.users"


urlpatterns = [
    path("update/", views.user_phone_update_view, name="update"),
    path("verify/", views.user_phone_verify_view, name="verify"),
]
