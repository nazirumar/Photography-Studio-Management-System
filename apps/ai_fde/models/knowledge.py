from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from pgvector.django import VectorField

from apps.core.models import BaseModel
from apps.studios.models import Studio


class KnowledgeDocument(BaseModel):
    """A studio-specific knowledge base document."""

    class DocumentType(models.TextChoices):
        POLICY = "policy", "Policy"
        PROCEDURE = "procedure", "Procedure"
        FAQ = "faq", "FAQ"
        GUIDE = "guide", "Guide"
        TEMPLATE = "template", "Template"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        ERROR = "error", "Error"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    studio = models.ForeignKey(
        Studio,
        on_delete=models.CASCADE,
        related_name="knowledge_documents",
    )
    title = models.CharField(max_length=300)
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    source = models.CharField(max_length=500, blank=True)
    content = models.TextField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    chunk_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="knowledge_documents_created",
    )

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"KnowledgeDocument {self.title}"


class KnowledgeChunk(BaseModel):
    """A chunked piece of a knowledge document with vector embedding."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        KnowledgeDocument,
        on_delete=models.CASCADE,
        related_name="chunks",
    )
    content = models.TextField()
    embedding = VectorField(dimensions=384, blank=True, null=True)
    chunk_index = models.PositiveIntegerField()
    metadata_json = models.JSONField(blank=True, null=True)

    class Meta(BaseModel.Meta):
        ordering = ["document", "chunk_index"]

    def __str__(self) -> str:
        return f"Chunk {self.chunk_index} of {self.document_id}"
