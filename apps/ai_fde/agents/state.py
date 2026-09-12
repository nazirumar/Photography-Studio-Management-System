from __future__ import annotations

import operator
from typing import Annotated, Any

from langgraph.graph import add_messages
from typing_extensions import TypedDict


class FDEState(TypedDict):
    conversation_id: str
    studio_id: str
    user_id: str
    user_message: str
    current_page: str | None
    current_entity_type: str | None
    current_entity_id: str | None
    intent: str | None
    messages: Annotated[list, add_messages]
    tool_calls: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]
    retrieved_documents: list[dict[str, Any]]
    proposed_action: dict[str, Any] | None
    requires_confirmation: bool
    final_response: dict[str, Any] | None
    errors: list[str]
    model_used: str | None
    total_tokens: int
