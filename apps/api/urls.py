from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views, new_api

router = DefaultRouter()
router.register(r"clients", views.ClientViewSet, basename="client")
router.register(r"bookings", views.BookingViewSet, basename="booking")
router.register(r"packages", views.PackageViewSet, basename="package")
router.register(r"invoices", views.InvoiceViewSet, basename="invoice")
router.register(r"payments", views.PaymentViewSet, basename="payment")
router.register(r"projects", views.ProjectViewSet, basename="project")

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/", views.dashboard_stats, name="dashboard_stats"),
    path("booking-requests/", new_api.create_booking_request_api, name="api_booking_requests"),
    path("contracts/", new_api.create_contract_api, name="api_contracts"),
    path("suppliers/", new_api.create_supplier_api, name="api_suppliers"),
    path("surveys/<uuid:pk>/submit/", new_api.submit_survey_api, name="api_survey_submit"),
]
