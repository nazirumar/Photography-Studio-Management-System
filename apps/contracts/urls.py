from django.urls import path
from . import views

app_name = "contracts"

urlpatterns = [
    path("", views.contract_list, name="list"),
    path("<uuid:pk>/", views.contract_detail, name="detail"),
    path("<uuid:pk>/preview/", views.contract_preview, name="preview"),
    path("booking/<uuid:booking_pk>/create/", views.contract_create, name="create"),
]
