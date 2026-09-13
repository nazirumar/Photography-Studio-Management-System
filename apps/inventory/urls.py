from django.urls import path

from . import views
from . import supplier_views

app_name = "inventory"

urlpatterns = [
    path("", views.inventory_list, name="list"),
    path("add/", views.inventory_create, name="create"),
    path("<uuid:pk>/", views.inventory_detail, name="detail"),
    path("<uuid:pk>/edit/", views.inventory_edit, name="edit"),
    path("<uuid:pk>/transaction/", views.inventory_transaction, name="transaction"),
    path("low-stock/", views.low_stock_list, name="low_stock"),
    path("suppliers/", supplier_views.supplier_list, name="supplier_list"),
    path("suppliers/add/", supplier_views.supplier_create, name="supplier_create"),
    path("suppliers/<uuid:pk>/", supplier_views.supplier_detail, name="supplier_detail"),
    path("suppliers/<uuid:pk>/edit/", supplier_views.supplier_edit, name="supplier_edit"),
    path("suppliers/<uuid:supplier_pk>/order/", supplier_views.supplier_order_create, name="supplier_order_create"),
    path("supplier-orders/<uuid:pk>/receive/", supplier_views.supplier_order_receive, name="supplier_order_receive"),
]
