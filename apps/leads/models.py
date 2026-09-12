from django.db import models

from apps.core.models import BaseModel


class Lead(BaseModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        FOLLOW_UP = "follow_up", "Follow-up"
        QUOTATION_SENT = "quotation_sent", "Quotation Sent"
        NEGOTIATING = "negotiating", "Negotiating"
        WON = "won", "Won"
        LOST = "lost", "Lost"

    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="leads")
    name = models.CharField(max_length=300)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    event_type = models.CharField(max_length=100, blank=True)
    expected_date = models.DateField(null=True, blank=True)
    estimated_budget = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    source = models.CharField(max_length=100, blank=True)
    assigned_to = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_leads"
    )
    notes = models.TextField(blank=True)
    next_follow_up = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    converted_client = models.ForeignKey(
        "clients.Client", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="converted_from_leads",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
