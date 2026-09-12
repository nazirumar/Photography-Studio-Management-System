from django.urls import path

from . import conflict_views

app_name = "bookings_conflicts"

urlpatterns = [
    path("api/check/", conflict_views.check_conflicts_api, name="check_conflicts"),
    path("api/photographers/", conflict_views.available_photographers_api, name="available_photographers"),
    path("api/equipment/", conflict_views.available_equipment_api, name="available_equipment"),
    path("", conflict_views.conflicts_dashboard, name="dashboard"),
]
