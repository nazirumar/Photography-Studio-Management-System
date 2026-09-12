from __future__ import annotations

import json
import logging
import time
from typing import Any

from openai import OpenAI, RateLimitError, APITimeoutError, APIError
from openai.types.chat import ChatCompletionMessageParam

from .provider import BaseLLMProvider

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60.0
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2.0


class OpenAIProvider(BaseLLMProvider):
    """OpenAI-compatible LLM provider. Works with OpenAI, Groq, and any OpenAI-compatible API."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None, timeout: float = DEFAULT_TIMEOUT):
        from django.conf import settings

        self._api_key = api_key or getattr(settings, "OPENAI_API_KEY", "")
        self._base_url = base_url or getattr(settings, "AI_BASE_URL", None)
        self._timeout = timeout
        self._client: OpenAI | None = None

    def _get_client(self) -> OpenAI:
        """Lazy-initialize the OpenAI client."""
        if self._client is None:
            kwargs: dict[str, Any] = {
                "api_key": self._api_key,
                "timeout": self._timeout,
                "max_retries": 0,
            }
            if self._base_url:
                kwargs["base_url"] = self._base_url
            self._client = OpenAI(**kwargs)
        return self._client

    def _call_with_retry(self, fn: Any, *args: Any, **kwargs: Any) -> Any:
        """Execute an API call with exponential backoff on rate limits."""
        last_exc: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return fn(*args, **kwargs)
            except RateLimitError as exc:
                last_exc = exc
                wait = RETRY_DELAY_BASE ** attempt
                logger.warning("Rate limit hit (attempt %d/%d). Retrying in %.1fs...", attempt, MAX_RETRIES, wait)
                time.sleep(wait)
            except APITimeoutError as exc:
                last_exc = exc
                wait = RETRY_DELAY_BASE ** attempt
                logger.warning("Request timed out (attempt %d/%d). Retrying in %.1fs...", attempt, MAX_RETRIES, wait)
                time.sleep(wait)
            except APIError as exc:
                logger.error("API error: %s", exc)
                raise
        if last_exc is not None:
            raise last_exc

    def generate(self, messages: list[dict], model: str | None = None, **kwargs) -> dict:
        """Generate a chat completion. Returns dict with 'content', 'model', 'usage'."""
        from django.conf import settings

        resolved_model = model or getattr(settings, "AI_PRIMARY_MODEL", "qwen/qwen3.6-27b")
        openai_messages = _coerce_messages(messages)

        kwargs.setdefault("max_tokens", 1024)

        try:
            client = self._get_client()
            response = self._call_with_retry(
                client.chat.completions.create,
                model=resolved_model,
                messages=openai_messages,
                **kwargs,
            )
            choice = response.choices[0] if response.choices else None
            content = choice.message.content if choice and choice.message else ""
            usage = {}
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            return {"content": content or "", "model": response.model, "usage": usage}
        except Exception:
            logger.exception("generate() failed for model %s", resolved_model)
            return {"content": "", "model": resolved_model, "usage": {}}

    def generate_structured(self, messages: list[dict], schema: dict, model: str | None = None, **kwargs) -> dict:
        """Generate structured JSON via function-calling."""
        from django.conf import settings

        resolved_model = model or getattr(settings, "AI_PRIMARY_MODEL", "qwen/qwen3.6-27b")
        openai_messages = _coerce_messages(messages)

        kwargs.setdefault("max_tokens", 1024)

        tool_definition = {
            "type": "function",
            "function": {
                "name": "structured_output",
                "description": "Return structured data matching the required schema.",
                "parameters": schema,
            },
        }

        try:
            client = self._get_client()
            response = self._call_with_retry(
                client.chat.completions.create,
                model=resolved_model,
                messages=openai_messages,
                tools=[tool_definition],
                tool_choice={"type": "function", "function": {"name": "structured_output"}},
                **kwargs,
            )
            choice = response.choices[0] if response.choices else None
            if not choice or not choice.message.tool_calls:
                logger.warning("No tool_calls in structured response for model %s", resolved_model)
                return {}

            tool_call = choice.message.tool_calls[0]
            args_raw = tool_call.function.arguments
            return json.loads(args_raw)
        except json.JSONDecodeError:
            logger.exception("Failed to parse structured response JSON for model %s", resolved_model)
            return {}
        except Exception:
            logger.exception("generate_structured() failed for model %s", resolved_model)
            return {}

    def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        """Generate embeddings. Returns list of vectors."""
        from django.conf import settings

        resolved_model = model or getattr(settings, "AI_EMBEDDING_MODEL", "text-embedding-3-small")
        if not texts:
            return []

        try:
            client = self._get_client()
            response = self._call_with_retry(
                client.embeddings.create,
                model=resolved_model,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception:
            logger.exception("embed() failed for model %s", resolved_model)
            return [[] for _ in texts]


def _coerce_messages(messages: list[dict]) -> list[ChatCompletionMessageParam]:
    """Convert message dicts to OpenAI-typed message params."""
    typed: list[ChatCompletionMessageParam] = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        typed.append({"role": role, "content": content})  # type: ignore[typeddict-item]
    return typed
