from django.urls import path

from . import views

app_name = "audit"

urlpatterns = [
    path("", views.audit_log_list, name="list"),
    path("<uuid:pk>/", views.audit_detail, name="detail"),
    path("entity/<str:entity_type>/<str:entity_id>/", views.audit_entity_history, name="entity_history"),
]
