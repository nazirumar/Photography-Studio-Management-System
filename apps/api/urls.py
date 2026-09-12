from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

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
]
