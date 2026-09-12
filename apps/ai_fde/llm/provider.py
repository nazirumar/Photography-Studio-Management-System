from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(
        self, messages: list[dict], model: str | None = None, **kwargs
    ) -> dict:
        """Generate a response from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            model: Optional model override. Uses provider default if None.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Dict with at least 'content' (str) and 'model' (str) keys.
            Returns None-level safe values on failure.
        """
        ...

    @abstractmethod
    def generate_structured(
        self, messages: list[dict], schema: dict, model: str | None = None, **kwargs
    ) -> dict:
        """Generate a structured (JSON) response from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            schema: JSON schema the response must conform to.
            model: Optional model override.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Dict containing the structured response matching the schema.
        """
        ...

    @abstractmethod
    def embed(
        self, texts: list[str], model: str | None = None
    ) -> list[list[float]]:
        """Generate embeddings for a list of texts.

        Args:
            texts: List of strings to embed.
            model: Optional embedding model override.

        Returns:
            List of embedding vectors (list of float lists).
        """
        ...
