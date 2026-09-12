from django.contrib import admin
from .models import Client
from .communication_models import Communication


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("display_name", "email", "phone", "studio", "status")
    list_filter = ("status", "studio")
    search_fields = ("first_name", "last_name", "email", "phone")


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ("client", "communication_type", "subject", "created_by", "created_at")
    list_filter = ("communication_type", "studio")
    search_fields = ("client__first_name", "client__last_name", "subject")
