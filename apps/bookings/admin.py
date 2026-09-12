from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("reference", "client", "date", "status", "payment_status", "total_amount", "studio")
    list_filter = ("status", "payment_status", "studio", "location_type")
    search_fields = ("reference", "client__first_name", "client__last_name", "title")
    date_hierarchy = "date"
    readonly_fields = ("package_snapshot", "created_at", "updated_at")
