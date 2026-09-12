from django.db import models

from apps.core.models import BaseModel

from .communication_models import Communication  # noqa: F401


class Client(BaseModel):
    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="clients")
    client_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    display_name = models.CharField(max_length=300, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    referral_source = models.CharField(max_length=100, blank=True)
    assigned_to = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_clients"
    )
    status = models.CharField(max_length=20, choices=[("active", "Active"), ("archived", "Archived")], default="active")
    tags = models.JSONField(default=list, blank=True)
    last_activity = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("studio", "client_number")]

    def __str__(self):
        return self.display_name or f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)
