from django.contrib import admin
from .models import ExpenseCategory, Expense


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "studio", "is_active")
    list_filter = ("is_active", "studio")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("reference", "description", "amount", "date", "payment_method", "studio")
    list_filter = ("payment_method", "studio", "category")
    search_fields = ("reference", "description", "vendor")
    date_hierarchy = "date"
