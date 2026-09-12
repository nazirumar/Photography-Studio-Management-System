from django.urls import path

from . import email_views

app_name = "notifications"

urlpatterns = [
    path("invoice/<uuid:pk>/send/", email_views.send_invoice, name="send_invoice"),
    path("receipt/<uuid:pk>/send/", email_views.send_receipt, name="send_receipt"),
    path("booking/<uuid:pk>/send/", email_views.send_booking_email, name="send_booking"),
    path("selection/<uuid:pk>/send/", email_views.send_selection_email, name="send_selection"),
    path("delivery/<uuid:pk>/send/", email_views.send_delivery_email_view, name="send_delivery"),
]
