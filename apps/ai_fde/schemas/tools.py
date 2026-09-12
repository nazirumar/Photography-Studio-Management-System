from __future__ import annotations

from pydantic import BaseModel, Field


class ToolDecision(BaseModel):
    """Represents the LLM's decision about which tool to invoke."""

    tool_name: str = Field(
        ...,
        description="The name of the tool or function to invoke.",
    )
    arguments: dict = Field(
        default_factory=dict,
        description="Key-value arguments to pass to the tool.",
    )
    reasoning_category: str = Field(
        ...,
        description=(
            "The category of reasoning that led to this decision "
            "(e.g. 'client_lookup', 'booking_check', 'finance_query')."
        ),
    )


class ProposedAction(BaseModel):
    """A proposed write action that may require user confirmation before execution."""

    action: str = Field(
        ...,
        description="The action identifier to execute (e.g. 'create_task', 'send_invoice').",
    )
    risk_level: str = Field(
        ...,
        description="Risk classification: 'low', 'medium', or 'high'.",
    )
    arguments: dict = Field(
        default_factory=dict,
        description="Arguments for the action.",
    )
    requires_confirmation: bool = Field(
        default=False,
        description="Whether the user must confirm before this action is executed.",
    )
