from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.core.models import BaseModel


class Feedback(BaseModel):
    """Client feedback/rating system."""
    class Rating(models.IntegerChoices):
        ONE = 1, "1 Star"
        TWO = 2, "2 Stars"
        THREE = 3, "3 Stars"
        FOUR = 4, "4 Stars"
        FIVE = 5, "5 Stars"

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="feedbacks"
    )
    client = models.ForeignKey(
        "clients.Client", on_delete=models.CASCADE, related_name="feedbacks"
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        choices=Rating.choices,
    )
    photography_quality = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        choices=Rating.choices,
        null=True,
        blank=True,
    )
    service_quality = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        choices=Rating.choices,
        null=True,
        blank=True,
    )
    delivery_speed = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        choices=Rating.choices,
        null=True,
        blank=True,
    )
    comment = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("project", "client")]

    def __str__(self):
        return f"Feedback from {self.client} - {self.rating}/5"

    @property
    def display_name(self):
        if self.is_anonymous:
            return "Anonymous"
        return self.client.display_name
