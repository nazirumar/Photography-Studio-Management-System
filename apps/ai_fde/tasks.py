from __future__ import annotations

import logging
from typing import Any

from celery import shared_task
from django.db import transaction

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def generate_daily_briefing(self: Any, studio_id: str) -> dict[str, Any]:
    """Generate a morning briefing for a studio and store/send it.

    This task is intended to be scheduled via Celery Beat for each active
    studio at the start of each business day.

    Args:
        studio_id: UUID of the studio.

    Returns:
        A dict with the briefing data.
    """
    from apps.ai_fde.services.briefing import generate_briefing_data
    from apps.studios.models import Studio

    try:
        studio = Studio.objects.get(id=studio_id)
    except Studio.DoesNotExist:
        logger.error("Studio %s not found for daily briefing", studio_id)
        return {"error": "Studio not found"}

    try:
        briefing = generate_briefing_data(studio)
        logger.info(
            "Generated daily briefing for studio %s: %d bookings today, "
            "%d overdue projects, outstanding ₦%.2f",
            studio_id,
            briefing["bookings_today_count"],
            briefing["overdue_projects_count"],
            briefing["outstanding_amount"],
        )
        return briefing

    except Exception as exc:
        logger.exception("Failed to generate briefing for studio %s", studio_id)
        raise self.retry(exc=exc) from exc


@shared_task
def cleanup_expired_proposals() -> dict[str, Any]:
    """Delete action proposals that have passed their expiry time.

    Intended to be run periodically via Celery Beat.

    Returns:
        A dict with the count of deleted proposals.
    """
    from django.utils import timezone

    from apps.ai_fde.models.action import AIActionProposal

    expired = AIActionProposal.objects.filter(
        status=AIActionProposal.Status.PENDING,
        expires_at__lte=timezone.now(),
    )
    count = expired.count()

    if count > 0:
        with transaction.atomic():
            expired.delete()
        logger.info("Cleaned up %d expired action proposals", count)

    return {"deleted_count": count}


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def ingest_knowledge_document(self: Any, document_id: str) -> dict[str, Any]:
    """Chunk and embed a knowledge document for RAG retrieval.

    Splits the document content into overlapping chunks, generates embeddings
    for each chunk, and stores them as ``KnowledgeChunk`` records.

    Args:
        document_id: UUID of the ``KnowledgeDocument`` to ingest.

    Returns:
        A dict with ingestion status and chunk count.
    """
    from apps.ai_fde.models.knowledge import KnowledgeChunk, KnowledgeDocument
    from apps.ai_fde.rag.embeddings import EmbeddingService

    try:
        document = KnowledgeDocument.objects.get(id=document_id)
    except KnowledgeDocument.DoesNotExist:
        logger.error("KnowledgeDocument %s not found", document_id)
        return {"error": "Document not found"}

    document.status = KnowledgeDocument.Status.PROCESSING
    document.save(update_fields=["status"])

    try:
        content = document.content
        if not content or not content.strip():
            document.status = KnowledgeDocument.Status.ERROR
            document.save(update_fields=["status"])
            return {"error": "Document has no content"}

        chunks = _split_into_chunks(content)

        embedder = EmbeddingService()
        embeddings = embedder.embed_texts([c["text"] for c in chunks])

        with transaction.atomic():
            document.chunks.all().delete()

            created_chunks = []
            for i, (chunk_data, embedding) in enumerate(zip(chunks, embeddings, strict=False)):
                created_chunks.append(
                    KnowledgeChunk(
                        document=document,
                        content=chunk_data["text"],
                        embedding=embedding if embedding else None,
                        chunk_index=i,
                        metadata_json={
                            "start_char": chunk_data["start"],
                            "end_char": chunk_data["end"],
                        },
                    )
                )

            KnowledgeChunk.objects.bulk_create(created_chunks, batch_size=100)

        document.chunk_count = len(created_chunks)
        document.status = KnowledgeDocument.Status.READY
        document.save(update_fields=["chunk_count", "status"])

        logger.info(
            "Ingested knowledge document %s: %d chunks created",
            document_id,
            len(created_chunks),
        )
        return {
            "status": "success",
            "document_id": document_id,
            "chunk_count": len(created_chunks),
        }

    except Exception as exc:
        logger.exception("Failed to ingest knowledge document %s", document_id)
        document.status = KnowledgeDocument.Status.ERROR
        document.save(update_fields=["status"])
        raise self.retry(exc=exc) from exc


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def _split_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict[str, Any]]:
    """Split text into overlapping chunks.

    Args:
        text: The full document text.
        chunk_size: Maximum characters per chunk.
        overlap: Number of overlapping characters between chunks.

    Returns:
        A list of dicts with ``text``, ``start``, and ``end`` keys.
    """
    chunks: list[dict[str, Any]] = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        # Try to break at a sentence boundary
        if end < len(text):
            for sep in ["\n\n", "\n", ". ", "! ", "? "]:
                last_sep = text.rfind(sep, start, end)
                if last_sep > start + chunk_size // 2:
                    end = last_sep + len(sep)
                    break

        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append({"text": chunk_text, "start": start, "end": end})

        start = end - overlap if end < len(text) else end

    return chunks
