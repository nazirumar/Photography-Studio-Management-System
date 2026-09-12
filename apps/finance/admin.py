from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "client", "total", "amount_paid", "balance", "status", "issue_date", "studio")
    list_filter = ("status", "studio")
    search_fields = ("invoice_number", "client__first_name", "client__last_name")
    date_hierarchy = "issue_date"
    readonly_fields = ("balance",)


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ("description", "invoice", "quantity", "unit_price", "total")
    list_filter = ("invoice__status", "invoice__studio")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "client", "amount", "payment_date", "method", "is_verified", "studio")
    list_filter = ("method", "is_verified", "studio")
    search_fields = ("reference", "client__first_name", "client__last_name")
    date_hierarchy = "payment_date"
    readonly_fields = ("reference",)
