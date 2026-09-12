from django.contrib import admin
from .models import PrintJob, FrameOrder, AlbumOrder


@admin.register(PrintJob)
class PrintJobAdmin(admin.ModelAdmin):
    list_display = ("project", "client", "print_size", "quantity", "status", "due_date")
    list_filter = ("status", "paper_type", "project__studio")
    date_hierarchy = "requested_date"


@admin.register(FrameOrder)
class FrameOrderAdmin(admin.ModelAdmin):
    list_display = ("project", "size", "frame_type", "quantity", "status", "due_date")
    list_filter = ("status", "orientation", "project__studio")


@admin.register(AlbumOrder)
class AlbumOrderAdmin(admin.ModelAdmin):
    list_display = ("project", "album_type", "pages", "design_status")
    list_filter = ("design_status", "project__studio")
