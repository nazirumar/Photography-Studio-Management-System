from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.inventory_list, name="list"),
    path("add/", views.inventory_create, name="create"),
    path("<uuid:pk>/", views.inventory_detail, name="detail"),
    path("<uuid:pk>/edit/", views.inventory_edit, name="edit"),
    path("<uuid:pk>/transaction/", views.inventory_transaction, name="transaction"),
    path("low-stock/", views.low_stock_list, name="low_stock"),
]
