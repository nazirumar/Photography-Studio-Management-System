from django.urls import path

from . import search_views

app_name = "core_search"

urlpatterns = [
    path("", search_views.global_search, name="global"),
]
