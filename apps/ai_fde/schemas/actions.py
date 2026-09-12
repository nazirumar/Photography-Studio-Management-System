from __future__ import annotations

from pydantic import BaseModel, Field


class CreateProjectTaskSchema(BaseModel):
    """Schema for creating a task within a project."""

    project_id: str = Field(..., description="ID of the project to add the task to.")
    title: str = Field(..., description="Task title.")
    description: str | None = Field(default=None, description="Optional task description.")
    assigned_to: str | None = Field(default=None, description="User ID or email of the assignee.")
    due_date: str | None = Field(default=None, description="Due date in ISO format (e.g. '2026-09-15').")
    priority: str | None = Field(default=None, description="Task priority: 'low', 'medium', 'high', or 'urgent'.")


class AddProjectNoteSchema(BaseModel):
    """Schema for adding a note to a project."""

    project_id: str = Field(..., description="ID of the project to add the note to.")
    notes: str = Field(..., description="The note content.")


class ChangeProjectPrioritySchema(BaseModel):
    """Schema for changing a project's priority."""

    project_id: str = Field(..., description="ID of the project to update.")
    priority: str = Field(..., description="New priority level: 'low', 'medium', 'high', or 'urgent'.")


class CreateReminderSchema(BaseModel):
    """Schema for creating a reminder."""

    title: str = Field(..., description="Reminder title.")
    due_date: str = Field(..., description="Due date in ISO format (e.g. '2026-09-15').")
    description: str | None = Field(default=None, description="Optional reminder description.")
    assigned_to: str | None = Field(default=None, description="User ID or email to assign the reminder to.")


# Phase 6: Operational Actions


class CreateClientSchema(BaseModel):
    """Schema for creating a new client."""

    first_name: str = Field(..., description="Client first name.")
    last_name: str = Field(..., description="Client last name.")
    phone: str | None = Field(default=None, description="Phone number.")
    email: str | None = Field(default=None, description="Email address.")
    whatsapp: str | None = Field(default=None, description="WhatsApp number.")
    notes: str | None = Field(default=None, description="Additional notes.")


class CreateLeadSchema(BaseModel):
    """Schema for creating a new lead."""

    name: str = Field(..., description="Lead name or company name.")
    phone: str | None = Field(default=None, description="Phone number.")
    email: str | None = Field(default=None, description="Email address.")
    event_type: str | None = Field(default=None, description="Type of event (e.g. 'wedding', 'portrait').")
    expected_date: str | None = Field(default=None, description="Expected event date (YYYY-MM-DD).")
    estimated_budget: float | None = Field(default=None, description="Estimated budget in Naira.")
    source: str | None = Field(default=None, description="Lead source (e.g. 'referral', 'instagram').")


class CreateBookingSchema(BaseModel):
    """Schema for creating a new booking."""

    client_id: str = Field(..., description="Client UUID.")
    package_id: str | None = Field(default=None, description="Package UUID.")
    event_type: str = Field(..., description="Event type (e.g. 'wedding', 'portrait').")
    date: str = Field(..., description="Booking date (YYYY-MM-DD).")
    start_time: str | None = Field(default=None, description="Start time (HH:MM).")
    location: str | None = Field(default=None, description="Event location.")
    title: str | None = Field(default=None, description="Booking title.")


class RescheduleBookingSchema(BaseModel):
    """Schema for rescheduling a booking."""

    booking_id: str = Field(..., description="Booking UUID.")
    new_date: str = Field(..., description="New date (YYYY-MM-DD).")
    new_time: str | None = Field(default=None, description="New time (HH:MM).")


class AssignPhotographerSchema(BaseModel):
    """Schema for assigning a photographer."""

    booking_id: str = Field(..., description="Booking UUID.")
    photographer_id: str = Field(..., description="User UUID of the photographer.")


class CreateDraftInvoiceSchema(BaseModel):
    """Schema for creating a draft invoice."""

    client_id: str = Field(..., description="Client UUID.")
    booking_id: str | None = Field(default=None, description="Optional booking UUID.")
    items: list[dict] = Field(..., description="List of {description, quantity, unit_price}.")
    due_date: str | None = Field(default=None, description="Due date (YYYY-MM-DD).")
    notes: str | None = Field(default=None, description="Invoice notes.")


# Phase 7: Financial Actions


class RecordPaymentSchema(BaseModel):
    """Schema for recording a payment."""

    client_id: str = Field(..., description="Client UUID.")
    amount: float = Field(..., description="Payment amount in Naira.")
    invoice_id: str | None = Field(default=None, description="Invoice UUID to pay against.")
    booking_id: str | None = Field(default=None, description="Booking UUID to pay against.")
    method: str = Field(..., description="Payment method: cash, bank_transfer, pos, card, online, other.")
    reference: str | None = Field(default=None, description="External reference number.")
    notes: str | None = Field(default=None, description="Payment notes.")


class RefundPaymentSchema(BaseModel):
    """Schema for refunding a payment."""

    payment_id: str = Field(..., description="Original payment UUID.")
    amount: float | None = Field(default=None, description="Refund amount (defaults to full).")
    reason: str = Field(..., description="Reason for the refund.")
    notes: str | None = Field(default=None, description="Additional notes.")


class CancelInvoiceSchema(BaseModel):
    """Schema for cancelling an invoice."""

    invoice_id: str = Field(..., description="Invoice UUID.")
    reason: str = Field(..., description="Reason for cancellation.")


class ApplyDiscountSchema(BaseModel):
    """Schema for applying a discount."""

    invoice_id: str = Field(..., description="Invoice UUID.")
    discount_amount: float = Field(..., description="Discount amount in Naira.")
    reason: str = Field(..., description="Reason for the discount.")
