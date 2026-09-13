from django.db import models

from apps.core.models import BaseModel


class Survey(BaseModel):
    """Post-shoot satisfaction survey."""
    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="surveys")
    booking = models.ForeignKey("bookings.Booking", on_delete=models.CASCADE, related_name="surveys")
    client_name = models.CharField(max_length=300)
    client_email = models.EmailField()
    nps_score = models.IntegerField(null=True, blank=True, help_text="0-10 NPS score")
    overall_rating = models.IntegerField(null=True, blank=True, help_text="1-5 stars")
    quality_rating = models.IntegerField(null=True, blank=True)
    service_rating = models.IntegerField(null=True, blank=True)
    value_rating = models.IntegerField(null=True, blank=True)
    would_recommend = models.BooleanField(null=True, blank=True)
    feedback_text = models.TextField(blank=True)
    improvements = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Survey: {self.client_name} - NPS {self.nps_score}"
