from django.urls import path

from . import health_views

app_name = "core_health"

urlpatterns = [
    path("celery/", health_views.celery_health_check, name="celery_health"),
    path("celery/tasks/", health_views.celery_task_status, name="celery_tasks"),
]
