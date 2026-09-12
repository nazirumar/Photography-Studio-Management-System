from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.ai_fde.models.conversation import AIConversation, AIMessage
from apps.core.models import BaseModel
from apps.studios.models import Studio


class AIToolExecution(BaseModel):
    """Records each AI tool invocation with risk classification and result."""

    class RiskClass(models.TextChoices):
        READ = "read", "Read"
        LOW_RISK_WRITE = "low_risk_write", "Low-Risk Write"
        HIGH_RISK_WRITE = "high_risk_write", "High-Risk Write"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        DENIED = "denied", "Denied"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.CASCADE,
        related_name="tool_executions",
    )
    message = models.ForeignKey(
        AIMessage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tool_executions",
    )
    studio = models.ForeignKey(
        Studio,
        on_delete=models.CASCADE,
        related_name="ai_tool_executions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_tool_executions",
    )
    tool_name = models.CharField(max_length=100)
    validated_arguments = models.JSONField(default=dict)
    risk_class = models.CharField(max_length=20, choices=RiskClass.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    duration_ms = models.IntegerField(null=True, blank=True)
    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"ToolExecution {self.tool_name} ({self.status})"


class AIActionProposal(BaseModel):
    """Proposed action that requires human approval before execution."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        EXPIRED = "expired", "Expired"
        EXECUTED = "executed", "Executed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    studio = models.ForeignKey(
        Studio,
        on_delete=models.CASCADE,
        related_name="ai_action_proposals",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_action_proposals",
    )
    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="action_proposals",
    )
    tool_name = models.CharField(max_length=100)
    arguments = models.JSONField(default=dict)
    risk_level = models.CharField(max_length=20)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    result = models.JSONField(null=True, blank=True)
    expires_at = models.DateTimeField()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"ActionProposal {self.tool_name} ({self.status})"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at
