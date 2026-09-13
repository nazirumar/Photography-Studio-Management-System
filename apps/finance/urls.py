from django.urls import path

from . import views, payment_views

app_name = "finance"

urlpatterns = [
    path("invoices/", views.invoice_list, name="invoice_list"),
    path("invoices/add/", views.invoice_create, name="invoice_create"),
    path("invoices/<uuid:pk>/", views.invoice_detail, name="invoice_detail"),
    path("invoices/<uuid:pk>/payment/", views.invoice_payment, name="invoice_payment"),
    path("invoices/<uuid:pk>/void/", views.invoice_void, name="invoice_void"),
    path("invoices/<uuid:pk>/preview/", views.invoice_preview, name="invoice_preview"),
    path("invoices/from-booking/<uuid:booking_pk>/", views.invoice_from_booking, name="invoice_from_booking"),
    path("payments/", views.payment_list, name="payment_list"),
    path("revenue/", views.revenue_report, name="revenue_report"),
    path("<uuid:pk>/pay/", payment_views.invoice_pay_online, name="invoice_pay_online"),
    path("pay/<uuid:pk>/", payment_views.payment_link_page, name="payment_link"),
    path("paystack/webhook/", payment_views.paystack_webhook, name="paystack_webhook"),
]
