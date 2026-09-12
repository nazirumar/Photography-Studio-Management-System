from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.core.models import BaseModel
from apps.studios.models import Studio


class AIConversation(BaseModel):
    """Represents a single AI conversation session."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    studio = models.ForeignKey(
        Studio,
        on_delete=models.CASCADE,
        related_name="ai_conversations",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_conversations",
    )
    title = models.CharField(max_length=200)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Conversation {self.id} - {self.title}"


class AIMessage(BaseModel):
    """A single message within an AI conversation."""

    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"
        SYSTEM = "system", "System"
        TOOL = "tool", "Tool"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField()
    tool_calls = models.JSONField(null=True, blank=True)
    tool_call_id = models.CharField(max_length=200, blank=True)

    class Meta(BaseModel.Meta):
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Message {self.id} ({self.role})"
