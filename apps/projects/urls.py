from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("", views.project_list, name="list"),
    path("add/", views.project_create, name="create"),
    path("<uuid:pk>/", views.project_detail, name="detail"),
    path("<uuid:pk>/edit/", views.project_edit, name="edit"),
    path("<uuid:pk>/status/", views.project_status_change, name="status"),
    path("<uuid:pk>/tasks/add/", views.task_create, name="task_create"),
    path("<uuid:pk>/tasks/<uuid:task_pk>/status/", views.task_status_change, name="task_status"),
]
