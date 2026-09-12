from django.urls import path

from . import sms_views

app_name = "sms"

urlpatterns = [
    path("send/", sms_views.send_sms_view, name="send"),
    path("send/bulk/", sms_views.send_bulk_sms, name="bulk"),
]
