from django.urls import path

from . import views

app_name = "expenses"

urlpatterns = [
    path("", views.expense_list, name="list"),
    path("add/", views.expense_create, name="create"),
    path("<uuid:pk>/edit/", views.expense_edit, name="edit"),
    path("<uuid:pk>/delete/", views.expense_delete, name="delete"),
    path("categories/", views.expense_category_list, name="categories"),
    path("categories/add/", views.expense_category_create, name="category_create"),
    path("summary/", views.expense_summary, name="summary"),
]
