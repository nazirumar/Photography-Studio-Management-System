from django.urls import path

from . import views

app_name = "packages"

urlpatterns = [
    path("", views.package_list, name="list"),
    path("add/", views.package_create, name="create"),
    path("<uuid:pk>/", views.package_detail, name="detail"),
    path("<uuid:pk>/edit/", views.package_edit, name="edit"),
    path("<uuid:pk>/toggle/", views.package_toggle, name="toggle"),
    path("categories/", views.category_list, name="categories"),
    path("categories/add/", views.category_create, name="category_create"),
]
