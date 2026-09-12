from django.contrib import admin
from .models import Equipment


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("asset_number", "name", "brand", "status", "assigned_to", "studio")
    list_filter = ("status", "studio")
    search_fields = ("asset_number", "name", "brand", "serial_number")
