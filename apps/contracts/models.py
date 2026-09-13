from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class Contract(BaseModel):
    """Booking contract with digital signature."""
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        SIGNED = "signed", "Signed"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="contracts")
    booking = models.ForeignKey("bookings.Booking", on_delete=models.CASCADE, related_name="contracts")
    contract_number = models.CharField(max_length=50)
    title = models.CharField(max_length=300, default="Photography Service Agreement")
    terms = models.TextField(blank=True, help_text="Contract terms and conditions")
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    client_signature = models.TextField(blank=True, help_text="Base64 encoded signature image")
    client_signed_at = models.DateTimeField(null=True, blank=True)
    studio_signature = models.TextField(blank=True)
    studio_signed_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("studio", "contract_number")]

    def __str__(self):
        return f"{self.contract_number} - {self.booking.reference}"
