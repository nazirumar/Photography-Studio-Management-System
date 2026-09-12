from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from apps.ai_fde.models.conversation import AIConversation, AIMessage

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from apps.accounts.models import User
    from apps.studios.models import Studio

logger = logging.getLogger(__name__)


def get_or_create_conversation(
    user: User,
    studio: Studio,
    conversation_id: str | None = None,
) -> AIConversation:
    """Return an existing conversation or create a new one.

    Args:
        user: The authenticated user.
        studio: The user's current studio.
        conversation_id: Optional UUID of an existing conversation.

    Returns:
        The existing or newly created ``AIConversation``.
    """
    if conversation_id:
        try:
            return AIConversation.objects.get(
                id=conversation_id, user=user, studio=studio
            )
        except AIConversation.DoesNotExist:
            logger.warning(
                "Conversation %s not found for user %s, creating new one",
                conversation_id,
                user.id,
            )

    conversation = AIConversation.objects.create(
        studio=studio,
        user=user,
        title="New Conversation",
    )
    return conversation


def get_conversations(user: User, studio: Studio) -> QuerySet[AIConversation]:
    """Return all conversations for a user within a studio, newest first."""
    return AIConversation.objects.filter(user=user, studio=studio).order_by(
        "-created_at"
    )


def add_message(
    conversation: AIConversation,
    role: str,
    content: str,
    tool_calls: list[dict[str, Any]] | None = None,
    tool_call_id: str | None = None,
) -> AIMessage:
    """Append a message to a conversation.

    Args:
        conversation: The parent conversation.
        role: One of ``AIMessage.Role`` values.
        content: The message text.
        tool_calls: Optional list of tool call dicts (for assistant messages).
        tool_call_id: Optional tool call ID (for tool-role messages).

    Returns:
        The created ``AIMessage``.
    """
    message = AIMessage.objects.create(
        conversation=conversation,
        role=role,
        content=content,
        tool_calls=tool_calls,
        tool_call_id=tool_call_id or "",
    )
    _update_conversation_title(conversation, role, content)
    return message


def get_messages(conversation: AIConversation) -> QuerySet[AIMessage]:
    """Return all messages for a conversation in chronological order."""
    return conversation.messages.order_by("created_at")


def serialize_messages(messages: QuerySet[AIMessage] | list[AIMessage]) -> list[dict[str, Any]]:
    """Serialize messages into the format expected by LLM chat APIs.

    Each dict contains ``role`` and ``content`` keys. Tool messages include
    ``tool_call_id`` and assistant messages may include ``tool_calls``.

    Args:
        messages: A queryset or list of ``AIMessage`` instances.

    Returns:
        A list of message dicts suitable for OpenAI chat completion input.
    """
    result: list[dict[str, Any]] = []
    for msg in messages:
        entry: dict[str, Any] = {
            "role": msg.role,
            "content": msg.content,
        }
        if msg.tool_calls:
            entry["tool_calls"] = msg.tool_calls
        if msg.tool_call_id:
            entry["tool_call_id"] = msg.tool_call_id
        result.append(entry)
    return result


def _update_conversation_title(
    conversation: AIConversation, role: str, content: str
) -> None:
    """Auto-generate a title from the first user message."""
    if conversation.title != "New Conversation":
        return
    if role != AIMessage.Role.USER:
        return

    title = content[:100].strip()
    if len(content) > 100:
        title = title.rsplit(" ", 1)[0] + "..."
    if title:
        conversation.title = title
        conversation.save(update_fields=["title"])
