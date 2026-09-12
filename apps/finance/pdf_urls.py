from django.urls import path

from . import pdf_views

app_name = "finance_pdf"

urlpatterns = [
    path("invoice/<uuid:pk>/pdf/", pdf_views.invoice_pdf, name="invoice_pdf"),
    path("booking/<uuid:pk>/quote/", pdf_views.quote_pdf, name="quote_pdf"),
]
