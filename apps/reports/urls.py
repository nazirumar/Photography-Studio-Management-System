from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_dashboard, name="dashboard"),
    path("revenue/", views.revenue_report, name="revenue"),
    path("expenses/", views.expense_report, name="expenses"),
    path("bookings/", views.booking_report, name="bookings"),
    path("clients/", views.client_report, name="clients"),
    path("leads/", views.lead_report, name="leads"),
    path("packages/", views.package_report, name="packages"),
    path("gallery/", views.gallery_report, name="gallery"),
    path("forecast/", views.revenue_forecast, name="forecast"),
]
