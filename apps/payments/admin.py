from django.contrib import admin
from .models import PaymentLink, WebhookLog


@admin.register(PaymentLink)
class PaymentLinkAdmin(admin.ModelAdmin):
    list_display = ("reference", "client", "amount", "paid", "is_active", "created_at")
    list_filter = ("paid", "is_active", "studio")
    search_fields = ("reference", "client__first_name", "client__last_name")
    date_hierarchy = "created_at"


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ("event_type", "processed", "created_at")
    list_filter = ("event_type", "processed")
    date_hierarchy = "created_at"
    readonly_fields = ("payload", "error_message")
