from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("", views.payment_link_list, name="link_list"),
    path("create/", views.payment_link_create, name="link_create"),
    path("<uuid:pk>/", views.payment_link_detail, name="link_detail"),
    path("pay/<str:reference>/", views.payment_link_public, name="public_pay"),
    path("verify/<str:reference>/", views.payment_verify, name="verify"),
    path("webhook/paystack/", views.paystack_webhook, name="webhook"),
]
