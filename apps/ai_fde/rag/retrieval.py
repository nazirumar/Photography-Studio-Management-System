from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from apps.ai_fde.models.knowledge import KnowledgeChunk

if TYPE_CHECKING:
    from apps.studios.models import Studio

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.5
DEFAULT_LIMIT = 5


class RAGRetriever:
    """Retrieval service for knowledge base queries using pgvector similarity search.

    Filters by studio for multi-tenancy isolation.
    """

    def search(
        self,
        query: str,
        studio: Studio,
        limit: int = DEFAULT_LIMIT,
    ) -> list[dict[str, Any]]:
        """Search for relevant knowledge chunks using cosine similarity.

        Args:
            query: The search query text.
            studio: The studio to scope results to.
            limit: Maximum number of results to return.

        Returns:
            A list of dicts with keys ``content``, ``similarity``,
            ``document_title``, ``document_type``, and ``chunk_id``.
            Sorted by similarity descending.
        """
        if not query or not query.strip():
            return []

        from apps.ai_fde.rag.embeddings import EmbeddingService

        embedder = EmbeddingService()
        query_vector = embedder.embed_text(query)

        if not query_vector:
            logger.warning("Failed to generate embedding for query, falling back to text search")
            return self._text_fallback(query, studio, limit)

        try:
            # pgvector cosine distance operator — lower distance = more similar
            # We fetch more than needed so we can filter by threshold
            chunks = (
                KnowledgeChunk.objects.filter(
                    document__studio=studio,
                    document__status="ready",
                    embedding__isnull=False,
                )
                .exclude(embedding=[])
                .select_related("document")
            )

            results: list[dict[str, Any]] = []
            for chunk in chunks:
                similarity = self._compute_similarity(query_vector, chunk.embedding)
                if similarity >= SIMILARITY_THRESHOLD:
                    results.append(
                        {
                            "chunk_id": str(chunk.id),
                            "content": chunk.content,
                            "similarity": round(similarity, 4),
                            "document_title": chunk.document.title,
                            "document_type": chunk.document.document_type,
                            "chunk_index": chunk.chunk_index,
                        }
                    )
                if len(results) >= limit:
                    break

            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:limit]

        except Exception:
            logger.exception("pgvector similarity search failed, falling back to text search")
            return self._text_fallback(query, studio, limit)

    def _text_fallback(
        self,
        query: str,
        studio: Studio,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Simple text-based fallback when vector search is unavailable.

        Uses PostgreSQL ``ILIKE`` for basic full-text matching.
        """
        chunks = (
            KnowledgeChunk.objects.filter(
                document__studio=studio,
                document__status="ready",
                content__icontains=query,
            )
            .select_related("document")[:limit]
        )

        return [
            {
                "chunk_id": str(chunk.id),
                "content": chunk.content,
                "similarity": 0.0,
                "document_title": chunk.document.title,
                "document_type": chunk.document.document_type,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
        ]

    @staticmethod
    def _compute_similarity(
        vector_a: list[float],
        vector_b: list[float],
    ) -> float:
        """Compute cosine similarity between two vectors.

        Returns a value between 0.0 (no similarity) and 1.0 (identical).
        """
        if not vector_a or not vector_b:
            return 0.0
        if len(vector_a) != len(vector_b):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vector_a, vector_b, strict=False))
        norm_a = sum(a * a for a in vector_a) ** 0.5
        norm_b = sum(b * b for b in vector_b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)
