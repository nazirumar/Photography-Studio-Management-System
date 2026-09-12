from django.urls import path

from . import communication_views

app_name = "client_comm"

urlpatterns = [
    path("<uuid:client_pk>/", communication_views.communication_list, name="list"),
    path("<uuid:client_pk>/add/", communication_views.communication_create, name="create"),
]
