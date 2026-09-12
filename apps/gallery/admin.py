from django.contrib import admin
from .models import Gallery, Photo, PhotoSelection


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "is_selection", "is_published")
    list_filter = ("is_selection", "is_published", "project__studio")


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("file_name", "gallery", "image_number", "is_selected", "is_edited", "is_delivered")
    list_filter = ("is_selected", "is_edited", "is_delivered", "gallery__project__studio")
    search_fields = ("file_name", "original_file_name")


@admin.register(PhotoSelection)
class PhotoSelectionAdmin(admin.ModelAdmin):
    list_display = ("photo", "client", "is_favourite", "finalized")
    list_filter = ("is_favourite", "finalized")
