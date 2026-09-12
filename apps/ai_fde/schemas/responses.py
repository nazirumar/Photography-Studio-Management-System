from __future__ import annotations

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field


class TextResponse(BaseModel):
    """Plain text response from the AI."""

    text: str = Field(..., description="The AI-generated text content.")


class MetricResponse(BaseModel):
    """A single metric data point."""

    label: str = Field(..., description="Display name for the metric.")
    value: str | float = Field(..., description="The metric value.")
    change: str | None = Field(
        default=None,
        description="Period-over-period change (e.g. '+12%', '-₦5,000').",
    )
    trend: str | None = Field(
        default=None,
        description="Trend direction: 'up', 'down', or 'flat'.",
    )


class MetricGroupResponse(BaseModel):
    """A titled group of related metrics."""

    title: str = Field(..., description="Section or group title.")
    metrics: list[MetricResponse] = Field(
        default_factory=list,
        description="List of metrics in this group.",
    )


class TableResponse(BaseModel):
    """Tabular data response."""

    headers: list[str] = Field(
        ..., description="Column headers for the table."
    )
    rows: list[list[str]] = Field(
        default_factory=list,
        description="Table rows, each a list of cell values.",
    )
    title: str | None = Field(
        default=None, description="Optional table title."
    )


class AlertResponse(BaseModel):
    """An alert or notification message."""

    message: str = Field(..., description="The alert message.")
    severity: Literal["info", "warning", "error"] = Field(
        ..., description="Alert severity level."
    )
    entity_type: str | None = Field(
        default=None,
        description="Type of entity the alert relates to (e.g. 'booking', 'invoice').",
    )
    entity_id: str | None = Field(
        default=None,
        description="ID of the related entity.",
    )


class ClientCardResponse(BaseModel):
    """Summary card for a client."""

    id: str = Field(..., description="Client ID.")
    name: str = Field(..., description="Client full name.")
    phone: str | None = Field(default=None, description="Phone number.")
    email: str | None = Field(default=None, description="Email address.")
    total_bookings: int | None = Field(
        default=None, description="Total number of bookings."
    )
    outstanding_balance: str | None = Field(
        default=None,
        description="Outstanding balance formatted as currency string.",
    )


class BookingCardResponse(BaseModel):
    """Summary card for a booking."""

    id: str = Field(..., description="Booking ID.")
    reference: str = Field(..., description="Booking reference code.")
    client: str = Field(..., description="Client name.")
    date: str = Field(..., description="Booking date (ISO format or display string).")
    event_type: str = Field(..., description="Type of event (e.g. 'wedding', 'portrait').")
    status: str = Field(..., description="Current booking status.")
    amount: str = Field(..., description="Total amount formatted as currency string.")


class ProjectCardResponse(BaseModel):
    """Summary card for a project."""

    id: str = Field(..., description="Project ID.")
    reference: str = Field(..., description="Project reference code.")
    client: str = Field(..., description="Client name.")
    status: str = Field(..., description="Current project status.")
    priority: str = Field(..., description="Project priority level.")
    days_remaining: int | None = Field(
        default=None, description="Days until project deadline."
    )
    progress_pct: int | None = Field(
        default=None, description="Completion percentage (0-100)."
    )


class InvoiceCardResponse(BaseModel):
    """Summary card for an invoice."""

    id: str = Field(..., description="Invoice ID.")
    number: str = Field(..., description="Invoice number.")
    client: str = Field(..., description="Client name.")
    amount: str = Field(..., description="Total amount formatted as currency string.")
    balance: str = Field(..., description="Outstanding balance formatted as currency string.")
    status: str = Field(..., description="Invoice status (e.g. 'draft', 'sent', 'paid').")
    due_date: str = Field(..., description="Due date (ISO format or display string).")


class ActionProposalResponse(BaseModel):
    """A proposed action that may require confirmation before execution."""

    proposal_id: str = Field(..., description="Unique identifier for this proposal.")
    action: str = Field(..., description="Action to execute (e.g. 'create_task').")
    description: str = Field(..., description="Human-readable description of the action.")
    risk_level: Literal["low", "medium", "high"] = Field(
        ..., description="Risk classification."
    )
    requires_confirmation: bool = Field(
        default=False,
        description="Whether user confirmation is needed.",
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional details or parameters for the action.",
    )


class KnowledgeAnswerResponse(BaseModel):
    """An answer sourced from the knowledge base."""

    answer: str = Field(..., description="The generated answer.")
    sources: list[str] = Field(
        default_factory=list,
        description="Source references used to generate the answer.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1.",
    )


class ErrorResponse(BaseModel):
    """An error response from the AI layer."""

    message: str = Field(..., description="Human-readable error message.")
    error_code: str | None = Field(
        default=None, description="Machine-readable error code."
    )
    details: str | None = Field(
        default=None, description="Additional error details or traceback summary."
    )


class ChatResponse(BaseModel):
    """A unified chat response that can carry any response type plus an AI explanation."""

    text: str = Field(
        default="",
        description="AI explanation or conversational text.",
    )
    data: (
        TextResponse
        | MetricResponse
        | MetricGroupResponse
        | TableResponse
        | AlertResponse
        | ClientCardResponse
        | BookingCardResponse
        | ProjectCardResponse
        | InvoiceCardResponse
        | ActionProposalResponse
        | KnowledgeAnswerResponse
        | ErrorResponse
        | None
    ) = Field(
        default=None,
        description="Optional structured data payload.",
    )
    response_type: str = Field(
        default="text",
        description="Type discriminator: 'text', 'metrics', 'table', 'alert', etc.",
    )
