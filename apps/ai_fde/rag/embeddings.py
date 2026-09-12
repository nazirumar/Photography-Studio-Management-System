from __future__ import annotations

import logging
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)

# Module-level cache for the fastembed model
_model: Any = None


def _get_model():
    """Lazy-load and cache the fastembed TextEmbedding model."""
    global _model
    if _model is None:
        from fastembed import TextEmbedding

        model_name = getattr(settings, "AI_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        logger.info("Loading embedding model: %s", model_name)
        _model = TextEmbedding(model_name=model_name)
        logger.info("Embedding model loaded")
    return _model


class EmbeddingService:
    """Service for generating text embeddings via fastembed (ONNX Runtime).

    Uses a quantized BAAI/bge-small-en-v1.5 model (384 dimensions).
    Runs entirely locally on CPU — no API key needed, no GPU required.
    """

    EMBEDDING_DIM = 384

    def __init__(self) -> None:
        pass

    def embed_text(self, text: str) -> list[float]:
        """Generate an embedding vector for a single text string."""
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return []

        try:
            model = _get_model()
            vectors = list(model.embed([text]))
            return vectors[0].tolist() if vectors else []
        except Exception:
            logger.exception("Failed to embed text (length=%d)", len(text))
            return []

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a batch of texts."""
        if not texts:
            return []

        try:
            model = _get_model()
            vectors = list(model.embed(texts))
            return [v.tolist() for v in vectors]
        except Exception:
            logger.exception("Failed to embed batch of %d texts", len(texts))
            return [[] for _ in texts]

    @staticmethod
    def dimension() -> int:
        """Return the embedding dimension (384)."""
        return 384
