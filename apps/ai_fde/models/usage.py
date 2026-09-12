from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.core.models import BaseModel
from apps.studios.models import Studio


class AIUsageLog(BaseModel):
    """Tracks token usage, latency, and cost per AI request."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    studio = models.ForeignKey(
        Studio,
        on_delete=models.CASCADE,
        related_name="ai_usage_logs",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_usage_logs",
    )
    model_name = models.CharField(max_length=100)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    tool_calls_count = models.PositiveIntegerField(default=0)
    latency_ms = models.PositiveIntegerField(default=0)
    estimated_cost_usd = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
    )
    error = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"UsageLog {self.model_name} - {self.created_at}"
