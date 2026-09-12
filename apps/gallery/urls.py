from django.urls import path

from . import views

app_name = "gallery"

urlpatterns = [
    path("<uuid:project_pk>/", views.gallery_list, name="list"),
    path("<uuid:project_pk>/add/", views.gallery_create, name="create"),
    path("<uuid:project_pk>/<uuid:pk>/", views.gallery_detail, name="detail"),
    path("<uuid:project_pk>/<uuid:gallery_pk>/upload/", views.photo_upload, name="photo_upload"),
    path(
        "<uuid:project_pk>/<uuid:gallery_pk>/<uuid:photo_pk>/select/",
        views.photo_toggle_selection,
        name="photo_select",
    ),
    path("<uuid:project_pk>/finalize/", views.selection_finalize, name="selection_finalize"),
    path("<uuid:project_pk>/stats/", views.selection_stats, name="selection_stats"),
]
