from django.urls import path

from . import upload_views

app_name = "gallery_upload"

urlpatterns = [
    path("<uuid:gallery_pk>/upload/", upload_views.upload_photos, name="upload"),
    path("photo/<uuid:pk>/delete/", upload_views.delete_photo, name="delete"),
]
