from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any

from django.db import transaction

if TYPE_CHECKING:
    import uuid

    from apps.ai_fde.models.knowledge import KnowledgeDocument

logger = logging.getLogger(__name__)


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict[str, Any]]:
    """Split text into chunks preserving paragraph boundaries.

    Tries to split on double-newlines first, then falls back to single
    newlines, then hard-cuts at chunk_size.

    Args:
        text: The source text to chunk.
        chunk_size: Target character length per chunk.
        overlap: Number of characters to overlap between consecutive chunks.

    Returns:
        A list of dicts with keys ``content`` and ``chunk_index``.
    """
    if not text or not text.strip():
        return []

    # Normalise whitespace
    cleaned = re.sub(r"\n{3,}", "\n\n", text.strip())

    # Split on paragraph boundaries
    paragraphs = re.split(r"\n\n+", cleaned)
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current) + len(para) + 2 <= chunk_size:
            current = f"{current}\n\n{para}" if current else para
        else:
            if current:
                chunks.append(current)
            # If a single paragraph exceeds chunk_size, hard-split it
            if len(para) > chunk_size:
                words = para.split()
                current = ""
                for word in words:
                    if len(current) + len(word) + 1 <= chunk_size:
                        current = f"{current} {word}" if current else word
                    else:
                        if current:
                            chunks.append(current)
                        current = word
            else:
                current = para

    if current:
        chunks.append(current)

    # Apply overlap: prepend the last `overlap` chars of the previous chunk
    if overlap > 0 and len(chunks) > 1:
        overlapped: list[str] = [chunks[0]]
        for i in range(1, len(chunks)):
            prev = chunks[i - 1]
            tail = prev[-overlap:]
            # Try to break at a word boundary
            space_idx = tail.find(" ")
            if space_idx > 0:
                tail = tail[space_idx + 1 :]
            overlapped.append(f"…{tail}\n\n{chunks[i]}")
        chunks = overlapped

    return [
        {"content": c, "chunk_index": idx}
        for idx, c in enumerate(chunks)
    ]


def ingest_document(document_id: str | uuid.UUID) -> dict[str, Any]:
    """Load, chunk, embed, and persist knowledge document chunks.

    Steps:
        1. Load ``KnowledgeDocument`` by PK.
        2. Chunk its content.
        3. Generate embeddings via ``EmbeddingService``.
        4. Create ``KnowledgeChunk`` records in bulk.
        5. Update document status to ``ready`` and set ``chunk_count``.

    Args:
        document_id: UUID of the ``KnowledgeDocument`` to ingest.

    Returns:
        A dict with ``status``, ``chunk_count``, and ``document_id``.
    """
    from apps.ai_fde.models.knowledge import KnowledgeChunk, KnowledgeDocument
    from apps.ai_fde.rag.embeddings import EmbeddingService

    result: dict[str, Any] = {
        "status": "error",
        "chunk_count": 0,
        "document_id": str(document_id),
    }

    try:
        doc: KnowledgeDocument = KnowledgeDocument.objects.get(pk=document_id)
    except KnowledgeDocument.DoesNotExist:
        logger.error("KnowledgeDocument %s not found", document_id)
        return result

    # Mark as processing
    doc.status = KnowledgeDocument.Status.PROCESSING
    doc.save(update_fields=["status", "updated_at"])

    try:
        # Chunk
        chunks = chunk_text(doc.content)
        if not chunks:
            doc.status = KnowledgeDocument.Status.ERROR
            doc.chunk_count = 0
            doc.save(update_fields=["status", "chunk_count", "updated_at"])
            result["error"] = "No chunks produced from document content"
            return result

        # Embed
        embedder = EmbeddingService()
        texts = [c["content"] for c in chunks]
        embeddings = embedder.embed_texts(texts)

        # Build KnowledgeChunk objects
        chunk_objects: list[KnowledgeChunk] = []
        for idx, chunk_data in enumerate(chunks):
            embedding = embeddings[idx] if idx < len(embeddings) else []
            chunk_objects.append(
                KnowledgeChunk(
                    document=doc,
                    content=chunk_data["content"],
                    chunk_index=chunk_data["chunk_index"],
                    embedding=embedding if embedding else None,
                    metadata_json={"source": doc.source, "document_type": doc.document_type},
                )
            )

        # Persist in a transaction
        with transaction.atomic():
            # Delete old chunks if re-ingesting
            KnowledgeChunk.objects.filter(document=doc).delete()
            KnowledgeChunk.objects.bulk_create(chunk_objects, batch_size=200)

        doc.status = KnowledgeDocument.Status.READY
        doc.chunk_count = len(chunk_objects)
        doc.save(update_fields=["status", "chunk_count", "updated_at"])

        result["status"] = "success"
        result["chunk_count"] = len(chunk_objects)
        logger.info(
            "Ingested document %s (%s) — %d chunks",
            doc.title,
            doc.id,
            len(chunk_objects),
        )

    except Exception:
        logger.exception("Failed to ingest document %s", document_id)
        doc.status = KnowledgeDocument.Status.ERROR
        doc.save(update_fields=["status", "updated_at"])
        result["error"] = "Ingestion failed — check logs"

    return result


def delete_document_chunks(document_id: str | uuid.UUID) -> int:
    """Delete all chunks belonging to a document.

    Args:
        document_id: UUID of the ``KnowledgeDocument`` whose chunks to remove.

    Returns:
        The number of chunks deleted.
    """
    from apps.ai_fde.models.knowledge import KnowledgeChunk

    count, _ = KnowledgeChunk.objects.filter(document_id=document_id).delete()
    logger.info("Deleted %d chunks for document %s", count, document_id)
    return count
