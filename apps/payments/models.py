import uuid
from decimal import Decimal

from django.db import models

from apps.core.models import BaseModel


class PaymentLink(BaseModel):
    """Generates shareable payment links for clients."""
    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="payment_links")
    invoice = models.ForeignKey("finance.Invoice", on_delete=models.SET_NULL, null=True, blank=True, related_name="payment_links")
    booking = models.ForeignKey("bookings.Booking", on_delete=models.SET_NULL, null=True, blank=True, related_name="payment_links")
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="payment_links")
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    description = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    paystack_reference = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment Link {self.reference} - {self.client.display_name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"PL-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class WebhookLog(BaseModel):
    """Logs all Paystack webhook events."""
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type} - {self.created_at}"
