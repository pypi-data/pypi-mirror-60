from django.urls import path

from ebay.notification.views import process_notification_api_view

app_name = "ebay.notification"


urlpatterns = [
    path("process/", process_notification_api_view, name="to_process"),
]
