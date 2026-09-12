from django.urls import path

from . import backup_views

app_name = "core_backup"

urlpatterns = [
    path("", backup_views.backup_list, name="list"),
    path("create/", backup_views.backup_create, name="create"),
    path("restore/<str:filename>/", backup_views.backup_restore, name="restore"),
]
