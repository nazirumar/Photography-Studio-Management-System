from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class Communication(BaseModel):
    TYPES = [
        ("call", "Call"),
        ("email", "Email"),
        ("meeting", "Meeting"),
        ("sms", "SMS"),
        ("whatsapp", "WhatsApp"),
        ("note", "Note"),
    ]

    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="communications")
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="communications")
    communication_type = models.CharField(max_length=20, choices=TYPES)
    subject = models.CharField(max_length=300)
    notes = models.TextField(blank=True)
    outcome = models.CharField(max_length=200, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_communication_type_display()} - {self.client.display_name}: {self.subject}"
