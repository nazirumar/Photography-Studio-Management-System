from django.urls import path

from . import views

app_name = "equipment"

urlpatterns = [
    path("", views.equipment_list, name="list"),
    path("add/", views.equipment_create, name="create"),
    path("<uuid:pk>/", views.equipment_detail, name="detail"),
    path("<uuid:pk>/edit/", views.equipment_edit, name="edit"),
    path("<uuid:pk>/status/", views.equipment_status_change, name="status"),
    path("<uuid:pk>/assign/", views.equipment_assign, name="assign"),
    path("<uuid:equipment_pk>/maintenance/add/", views.maintenance_log_add, name="maintenance_add"),
    path("<uuid:equipment_pk>/maintenance/logs/", views.maintenance_log_list, name="maintenance_logs"),
    path("maintenance/", views.maintenance_due_list, name="maintenance"),
]
