from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class Notification(BaseModel):
    class Type(models.TextChoices):
        BOOKING_REMINDER = "booking_reminder", "Booking Reminder"
        DEPOSIT_DUE = "deposit_due", "Deposit Due"
        DELIVERY_DUE = "delivery_due", "Delivery Due"
        SELECTION_READY = "selection_ready", "Selection Ready"
        EDITING_COMPLETE = "editing_complete", "Editing Complete"
        PRINT_READY = "print_ready", "Print Ready"
        LOW_STOCK = "low_stock", "Low Stock"
        MAINTENANCE_DUE = "maintenance_due", "Maintenance Due"
        PAYMENT_RECEIVED = "payment_received", "Payment Received"
        GENERAL = "general", "General"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=30, choices=Type.choices, default=Type.GENERAL, db_index=True)
    title = models.CharField(max_length=300)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    link = models.CharField(max_length=500, blank=True)
    entity_type = models.CharField(max_length=100, blank=True)
    entity_id = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user}"


class SMSDeliveryLog(BaseModel):
    """Track SMS delivery status from Termii."""
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="sms_logs")
    phone = models.CharField(max_length=20)
    message = models.TextField()
    termii_message_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    sent_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="sms_logs"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"SMS to {self.phone} - {self.status}"
