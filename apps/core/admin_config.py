from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.accounts.models import User, StaffProfile
from apps.clients.models import Client
from apps.bookings.models import Booking, BookingRequest
from apps.finance.models import Invoice, InvoiceItem, Payment, PaymentReminder
from apps.packages.models import Package, PackageAddon, ServiceCategory
from apps.leads.models import Lead
from apps.projects.models import Project
from apps.gallery.models import Gallery
from apps.inventory.models import InventoryItem, StockTransaction, Supplier, SupplierOrder
from apps.equipment.models import Equipment
from apps.printing.models import PrintJob, FrameOrder, AlbumOrder, PrintPriceList
from apps.notifications.models import Notification, SMSDeliveryLog
from apps.expenses.models import Expense, ExpenseCategory
from apps.audit.models import AuditLog
from apps.studios.models import Studio
from apps.contracts.models import Contract
from apps.feedback.models import Survey
from apps.staff.models import StaffSchedule, StaffBooking
from apps.portal.models import ClientUser


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "first_name", "last_name", "is_staff", "is_active"]
    list_filter = ["is_staff", "is_active"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["email"]
    fieldsets = BaseUserAdmin.fieldsets
    add_fieldsets = BaseUserAdmin.add_fieldsets


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "studio", "role", "phone"]
    list_filter = ["role", "studio"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["display_name", "email", "phone", "studio", "status", "created_at"]
    list_filter = ["status", "studio"]
    search_fields = ["first_name", "last_name", "email", "phone"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ClientUser)
class ClientUserAdmin(admin.ModelAdmin):
    list_display = ["email", "first_name", "last_name", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["email", "first_name", "last_name"]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "status", "source", "created_at"]
    list_filter = ["status", "source"]
    search_fields = ["name", "email", "phone"]


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "deposit_percentage", "is_active", "studio"]
    list_filter = ["is_active", "studio"]
    search_fields = ["name"]


@admin.register(PackageAddon)
class PackageAddonAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "package"]
    list_filter = ["package"]


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "studio"]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["reference", "client", "package", "date", "status", "payment_status", "total_amount"]
    list_filter = ["status", "payment_status", "studio"]
    search_fields = ["reference", "client__first_name", "client__last_name"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "date"


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email", "event_type", "preferred_date", "status"]
    list_filter = ["status", "studio"]
    search_fields = ["first_name", "last_name", "email"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["reference", "client", "status", "due_date"]
    list_filter = ["status"]
    search_fields = ["reference", "client__first_name", "client__last_name"]


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "created_at"]
    search_fields = ["title"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "client", "total", "amount_paid", "balance", "status", "issue_date"]
    list_filter = ["status", "studio"]
    search_fields = ["invoice_number", "client__first_name", "client__last_name"]
    date_hierarchy = "issue_date"


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ["invoice", "description", "quantity", "unit_price", "total"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["reference", "client", "amount", "method", "payment_date", "is_verified"]
    list_filter = ["method", "is_verified", "studio"]
    search_fields = ["reference", "client__first_name", "client__last_name"]
    date_hierarchy = "payment_date"


@admin.register(PaymentReminder)
class PaymentReminderAdmin(admin.ModelAdmin):
    list_display = ["invoice", "reminder_type", "sent_via", "sent_at"]
    list_filter = ["reminder_type", "sent_via"]


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ["contract_number", "booking", "total_amount", "status", "created_at"]
    list_filter = ["status", "studio"]
    search_fields = ["contract_number"]


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ["client_name", "nps_score", "overall_rating", "is_completed", "created_at"]
    list_filter = ["is_completed", "studio"]
    search_fields = ["client_name", "client_email"]


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ["sku", "name", "category", "quantity", "reorder_level", "is_active"]
    list_filter = ["category", "is_active", "studio"]
    search_fields = ["sku", "name"]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name", "contact_person", "phone", "city", "is_active"]
    list_filter = ["is_active", "studio"]
    search_fields = ["name", "contact_person"]


@admin.register(SupplierOrder)
class SupplierOrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "supplier", "item_name", "quantity", "total_cost", "status"]
    list_filter = ["status", "studio"]
    search_fields = ["order_number", "item_name"]


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ["item", "transaction_type", "quantity", "reference", "created_at"]
    list_filter = ["transaction_type"]
    date_hierarchy = "created_at"


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ["name", "brand", "model", "status", "studio"]
    list_filter = ["status", "studio"]
    search_fields = ["name", "brand", "model"]


@admin.register(PrintJob)
class PrintJobAdmin(admin.ModelAdmin):
    list_display = ["reference", "project", "status", "quantity", "created_at"]
    list_filter = ["status", "studio"]


@admin.register(FrameOrder)
class FrameOrderAdmin(admin.ModelAdmin):
    list_display = ["reference", "project", "status", "created_at"]
    list_filter = ["status"]


@admin.register(AlbumOrder)
class AlbumOrderAdmin(admin.ModelAdmin):
    list_display = ["reference", "project", "status", "created_at"]
    list_filter = ["status"]


@admin.register(PrintPriceList)
class PrintPriceListAdmin(admin.ModelAdmin):
    list_display = ["name", "product_type", "size", "selling_price", "is_active"]
    list_filter = ["product_type", "is_active"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["description", "amount", "category", "date", "studio"]
    list_filter = ["category", "studio"]
    search_fields = ["description"]
    date_hierarchy = "date"


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "studio"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "notification_type", "is_read", "created_at"]
    list_filter = ["notification_type", "is_read"]


@admin.register(SMSDeliveryLog)
class SMSDeliveryLogAdmin(admin.ModelAdmin):
    list_display = ["phone", "status", "sent_at", "delivered_at"]
    list_filter = ["status", "studio"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "entity_type", "entity_id", "created_at"]
    list_filter = ["action", "entity_type"]
    search_fields = ["entity_id"]
    date_hierarchy = "created_at"
    readonly_fields = ["user", "action", "entity_type", "entity_id", "before_values", "after_values", "created_at"]


@admin.register(StaffSchedule)
class StaffScheduleAdmin(admin.ModelAdmin):
    list_display = ["staff", "day_of_week", "start_time", "end_time", "is_available"]
    list_filter = ["day_of_week", "is_available"]


@admin.register(StaffBooking)
class StaffBookingAdmin(admin.ModelAdmin):
    list_display = ["staff", "booking", "role", "created_at"]
    search_fields = ["staff__email", "booking__reference"]
