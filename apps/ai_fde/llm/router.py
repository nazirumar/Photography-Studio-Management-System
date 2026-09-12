from __future__ import annotations

import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class ModelRouter:
    """Deterministic router that maps intents to model roles."""

    FAST = "fast"
    PRIMARY = "primary"
    REASONING = "reasoning"
    EMBEDDING = "embedding"

    _INTENT_MAP: dict[str, str] = {
        "classify": "fast",
        "categorize": "fast",
        "tag": "fast",
        "summarize": "fast",
        "extract": "fast",
        "analyze": "reasoning",
        "plan": "reasoning",
        "reason": "reasoning",
        "evaluate": "reasoning",
        "compare": "reasoning",
    }

    def __init__(self) -> None:
        self._models: dict[str, str] = {
            self.FAST: getattr(settings, "AI_FAST_MODEL", "qwen/qwen3.6-27b"),
            self.PRIMARY: getattr(settings, "AI_PRIMARY_MODEL", "qwen/qwen3.6-27b"),
            self.REASONING: getattr(
                settings, "AI_REASONING_MODEL", "qwen/qwen3.6-27b"
            ),
            self.EMBEDDING: getattr(
                settings, "AI_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"
            ),
        }
        logger.debug("ModelRouter initialized: %s", self._models)

    def route(self, intent: str) -> str:
        """Return the model name appropriate for the given intent.

        Args:
            intent: A lowercase intent string (e.g. 'classify', 'analyze').

        Returns:
            The model name string for the resolved role.
        """
        role = self._INTENT_MAP.get(intent, self.PRIMARY)
        return self._models[role]

    def get_model(self, role: str) -> str:
        """Return the model name for a specific role.

        Args:
            role: One of 'fast', 'primary', 'reasoning', 'embedding'.

        Returns:
            The model name string. Falls back to primary if role is unknown.
        """
        return self._models.get(role, self._models[self.PRIMARY])
