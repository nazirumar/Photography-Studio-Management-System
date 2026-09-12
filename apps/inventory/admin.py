from django.contrib import admin
from .models import InventoryItem, StockTransaction


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "category", "quantity", "unit", "reorder_level", "is_active", "studio")
    list_filter = ("is_active", "studio", "category")
    search_fields = ("sku", "name", "supplier")


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ("item", "transaction_type", "quantity", "reference", "performed_by", "created_at")
    list_filter = ("transaction_type", "item__studio")
    date_hierarchy = "created_at"
