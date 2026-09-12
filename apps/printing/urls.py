from django.urls import path

from . import views

app_name = "printing"

urlpatterns = [
    path("", views.printing_dashboard, name="dashboard"),
    path("print-job/<uuid:project_pk>/add/", views.print_job_create, name="print_job_create"),
    path("print-job/<uuid:pk>/status/", views.print_job_status, name="print_job_status"),
    path("frame/<uuid:project_pk>/add/", views.frame_order_create, name="frame_order_create"),
    path("frame/<uuid:pk>/status/", views.frame_order_status, name="frame_order_status"),
    path("album/<uuid:project_pk>/add/", views.album_order_create, name="album_order_create"),
    path("album/<uuid:pk>/status/", views.album_order_status, name="album_order_status"),
    path("album/<uuid:pk>/approve/", views.album_approve, name="album_approve"),
]
