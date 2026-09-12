from django.urls import path

from . import export_views

app_name = "core_export"

urlpatterns = [
    path("clients/", export_views.export_clients_csv, name="clients_csv"),
    path("bookings/", export_views.export_bookings_csv, name="bookings_csv"),
    path("invoices/", export_views.export_invoices_csv, name="invoices_csv"),
    path("expenses/", export_views.export_expenses_csv, name="expenses_csv"),
    path("clients/import/", export_views.export_clients_import, name="clients_import"),
]
