from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "entity_type", "entity_id", "user", "timestamp")
    list_filter = ("action", "entity_type", "timestamp")
    search_fields = ("entity_id", "user__email")
    date_hierarchy = "timestamp"
    readonly_fields = ("user", "action", "entity_type", "entity_id", "before_values", "after_values", "ip_address", "timestamp")
