from django.contrib import admin
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "event_type", "status", "assigned_to", "studio")
    list_filter = ("status", "source", "studio")
    search_fields = ("name", "email", "phone")
    date_hierarchy = "created_at"
