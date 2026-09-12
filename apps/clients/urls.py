from django.urls import path

from . import views

app_name = "clients"

urlpatterns = [
    path("", views.client_list, name="list"),
    path("add/", views.client_create, name="create"),
    path("<uuid:pk>/", views.client_detail, name="detail"),
    path("<uuid:pk>/edit/", views.client_edit, name="edit"),
    path("<uuid:pk>/archive/", views.client_archive, name="archive"),
]
