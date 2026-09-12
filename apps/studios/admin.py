from django.contrib import admin
from .models import Studio


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "email", "phone")
    readonly_fields = ("created_at", "updated_at")
