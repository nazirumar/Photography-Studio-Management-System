from __future__ import annotations

import uuid

from django.db import models

from apps.ai_fde.models.conversation import AIConversation
from apps.core.models import BaseModel


class FDEContext(BaseModel):
    """Stores page and entity context for context-aware AI conversations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.CASCADE,
        related_name="fde_contexts",
    )
    current_page = models.CharField(max_length=100, blank=True)
    current_entity_type = models.CharField(max_length=50, blank=True)
    current_entity_id = models.UUIDField(null=True, blank=True)
    metadata_json = models.JSONField(blank=True, null=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"FDEContext {self.id} - {self.current_page}"
