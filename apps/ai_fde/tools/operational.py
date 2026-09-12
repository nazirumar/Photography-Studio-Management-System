"""Phase 6: Operational write tools. All require human confirmation."""
from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from .base import FDEContext, fde_tool

logger = logging.getLogger(__name__)


def _generate_number(prefix: str, qs: Any, field: str, studio: Any) -> str:
    last = qs.filter(studio=studio).order_by("-created_at").first()
    num = 1
    if last and getattr(last, field, None):
        try:
            num = int(getattr(last, field).split("-")[-1]) + 1
        except (ValueError, IndexError):
            num = qs.filter(studio=studio).count() + 1
    return f"{prefix}-{num:04d}"


def _safe_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


@fde_tool(
    name="create_client",
    permission="clients.add_client",
    risk="high_risk_write",
    description="Create a new client in the studio. Requires confirmation. Params: first_name (required), last_name (required), phone (optional), email (optional), whatsapp (optional), notes (optional).",
)
def create_client(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    from apps.clients.models import Client

    first_name = params.get("first_name", "").strip()
    last_name = params.get("last_name", "").strip()
    if not first_name or not last_name:
        return {"success": False, "error": "first_name and last_name are required."}

    client_number = _generate_number("CL", Client.objects, "client_number", context.studio)

    client = Client.objects.create(
        studio=context.studio,
        client_number=client_number,
        first_name=first_name,
        last_name=last_name,
        phone=params.get("phone", ""),
        email=params.get("email", ""),
        whatsapp=params.get("whatsapp", ""),
        notes=params.get("notes", ""),
        assigned_to=context.user,
    )

    return {
        "success": True,
        "client_id": str(client.pk),
        "client_number": client.client_number,
        "display_name": client.display_name,
        "message": f"Client {client.display_name} created successfully.",
    }


@fde_tool(
    name="create_lead",
    permission="leads.add_lead",
    risk="high_risk_write",
    description="Create a new lead. Requires confirmation. Params: name (required), phone (optional), email (optional), event_type (optional), expected_date (optional YYYY-MM-DD), estimated_budget (optional), source (optional).",
)
def create_lead(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    from apps.leads.models import Lead

    name = params.get("name", "").strip()
    if not name:
        return {"success": False, "error": "name is required."}

    lead = Lead.objects.create(
        studio=context.studio,
        name=name,
        phone=params.get("phone", ""),
        email=params.get("email", ""),
        whatsapp=params.get("whatsapp", ""),
        event_type=params.get("event_type", ""),
        source=params.get("source", "ai_fde"),
        notes=params.get("notes", ""),
        assigned_to=context.user,
    )

    update_fields: list[str] = []

    expected_date_str = params.get("expected_date")
    if expected_date_str:
        try:
            lead.expected_date = date.fromisoformat(expected_date_str)
            update_fields.append("expected_date")
        except (ValueError, TypeError):
            pass

    budget = _safe_decimal(params.get("estimated_budget"))
    if budget is not None:
        lead.estimated_budget = budget
        update_fields.append("estimated_budget")

    if update_fields:
        lead.save(update_fields=update_fields)

    return {
        "success": True,
        "lead_id": str(lead.pk),
        "name": lead.name,
        "message": f"Lead '{lead.name}' created successfully.",
    }


@fde_tool(
    name="create_booking",
    permission="bookings.add_booking",
    risk="high_risk_write",
    description="Create a new booking. Requires confirmation. Params: client_id (required), package_id (optional), event_type (required), date (required YYYY-MM-DD), start_time (optional HH:MM), location (optional), title (optional).",
)
def create_booking(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    from apps.bookings.models import Booking
    from apps.clients.models import Client
    from apps.packages.models import Package

    client_id = params.get("client_id")
    event_type = params.get("event_type", "")
    booking_date_str = params.get("date", "")

    if not client_id or not event_type or not booking_date_str:
        return {"success": False, "error": "client_id, event_type, and date are required."}

    try:
        client = Client.objects.get(pk=client_id, studio=context.studio)
    except Client.DoesNotExist:
        return {"success": False, "error": "Client not found."}

    try:
        booking_date = date.fromisoformat(booking_date_str)
    except ValueError:
        return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD."}

    reference = _generate_number(
        context.studio.booking_prefix, Booking.objects, "reference", context.studio
    )

    package = None
    package_snapshot: dict[str, Any] = {}
    total_amount = Decimal("0")
    deposit_required = Decimal("0")

    package_id = params.get("package_id")
    if package_id:
        try:
            package = Package.objects.get(pk=package_id, studio=context.studio)
            total_amount = package.price
            deposit_pct = package.deposit_percentage or context.studio.default_deposit_percentage or Decimal("50")
            deposit_required = total_amount * deposit_pct / 100
            package_snapshot = {
                "name": package.name,
                "price": str(package.price),
                "deposit_percentage": str(deposit_pct),
            }
        except Package.DoesNotExist:
            pass

    booking = Booking.objects.create(
        studio=context.studio,
        reference=reference,
        client=client,
        package=package,
        event_type=event_type,
        title=params.get("title", f"{client.display_name} - {event_type}"),
        date=booking_date,
        start_time=params.get("start_time") or None,
        location=params.get("location", ""),
        total_amount=total_amount,
        deposit_required=deposit_required,
        package_snapshot=package_snapshot,
        status=Booking.Status.ENQUIRY,
        created_by=context.user,
    )

    return {
        "success": True,
        "booking_id": str(booking.pk),
        "reference": booking.reference,
        "client": client.display_name,
        "date": str(booking.date),
        "amount": str(booking.total_amount),
        "message": f"Booking {booking.reference} created for {client.display_name}.",
    }


@fde_tool(
    name="reschedule_booking",
    permission="bookings.change_booking",
    risk="high_risk_write",
    description="Reschedule a booking to a new date/time. Requires confirmation. Params: booking_id (required), new_date (required YYYY-MM-DD), new_time (optional HH:MM).",
)
def reschedule_booking(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    from apps.bookings.models import Booking

    booking_id = params.get("booking_id")
    new_date_str = params.get("new_date", "")

    if not booking_id or not new_date_str:
        return {"success": False, "error": "booking_id and new_date are required."}

    try:
        booking = Booking.objects.get(pk=booking_id, studio=context.studio)
    except Booking.DoesNotExist:
        return {"success": False, "error": "Booking not found."}

    try:
        new_date = date.fromisoformat(new_date_str)
    except ValueError:
        return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD."}

    old_date = booking.date
    old_time = booking.start_time

    booking.date = new_date
    new_time = params.get("new_time")
    if new_time:
        booking.start_time = new_time
    booking.save(update_fields=["date", "start_time", "updated_at"])

    return {
        "success": True,
        "booking_id": str(booking.pk),
        "reference": booking.reference,
        "old_date": str(old_date),
        "old_time": str(old_time) if old_time else None,
        "new_date": str(new_date),
        "new_time": str(booking.start_time) if booking.start_time else None,
        "message": f"Booking {booking.reference} rescheduled from {old_date} to {new_date}.",
    }


@fde_tool(
    name="assign_photographer",
    permission="bookings.change_booking",
    risk="high_risk_write",
    description="Assign a photographer to a booking. Requires confirmation. Params: booking_id (required), photographer_id (required - user ID).",
)
def assign_photographer(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    from apps.accounts.models import User
    from apps.bookings.models import Booking

    booking_id = params.get("booking_id")
    photographer_id = params.get("photographer_id")

    if not booking_id or not photographer_id:
        return {"success": False, "error": "booking_id and photographer_id are required."}

    try:
        booking = Booking.objects.get(pk=booking_id, studio=context.studio)
    except Booking.DoesNotExist:
        return {"success": False, "error": "Booking not found."}

    try:
        photographer = User.objects.get(pk=photographer_id, studio=context.studio)
    except User.DoesNotExist:
        return {"success": False, "error": "Photographer not found."}

    booking.photographer = photographer
    booking.save(update_fields=["photographer", "updated_at"])

    display = photographer.get_full_name() or photographer.email
    return {
        "success": True,
        "booking_id": str(booking.pk),
        "reference": booking.reference,
        "photographer": display,
        "message": f"Assigned {display} to booking {booking.reference}.",
    }


@fde_tool(
    name="create_draft_invoice",
    permission="finance.add_invoice",
    risk="high_risk_write",
    description="Create a draft invoice for a client. Requires confirmation. Params: client_id (required), booking_id (optional), items (required - list of {description, quantity, unit_price}), due_date (optional YYYY-MM-DD), notes (optional).",
)
def create_draft_invoice(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    from apps.clients.models import Client
    from apps.finance.models import Invoice, InvoiceItem

    client_id = params.get("client_id")
    items = params.get("items", [])

    if not client_id:
        return {"success": False, "error": "client_id is required."}
    if not items:
        return {"success": False, "error": "At least one item is required."}

    try:
        client = Client.objects.get(pk=client_id, studio=context.studio)
    except Client.DoesNotExist:
        return {"success": False, "error": "Client not found."}

    invoice_number = _generate_number(
        context.studio.invoice_prefix, Invoice.objects, "invoice_number", context.studio
    )

    subtotal = Decimal("0")
    invoice_items: list[dict[str, Any]] = []
    for item in items:
        desc = item.get("description", "")
        qty = Decimal(str(item.get("quantity", 1)))
        price = Decimal(str(item.get("unit_price", 0)))
        line_total = qty * price
        subtotal += line_total
        invoice_items.append({
            "description": desc,
            "quantity": qty,
            "unit_price": price,
            "total": line_total,
        })

    tax_rate = context.studio.tax_rate or Decimal("0")
    tax = subtotal * tax_rate / 100

    invoice = Invoice.objects.create(
        studio=context.studio,
        invoice_number=invoice_number,
        client=client,
        issue_date=date.today(),
        subtotal=subtotal,
        tax=tax,
        total=subtotal + tax,
        status=Invoice.Status.DRAFT,
        notes=params.get("notes", ""),
    )

    booking_id = params.get("booking_id")
    if booking_id:
        from apps.bookings.models import Booking

        try:
            booking = Booking.objects.get(pk=booking_id, studio=context.studio)
            invoice.booking = booking
            invoice.save(update_fields=["booking"])
        except Booking.DoesNotExist:
            pass

    due_date_str = params.get("due_date")
    if due_date_str:
        try:
            invoice.due_date = date.fromisoformat(due_date_str)
            invoice.save(update_fields=["due_date"])
        except (ValueError, TypeError):
            pass

    for item_data in invoice_items:
        InvoiceItem.objects.create(
            invoice=invoice,
            description=item_data["description"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            total=item_data["total"],
        )

    return {
        "success": True,
        "invoice_id": str(invoice.pk),
        "invoice_number": invoice.invoice_number,
        "client": client.display_name,
        "subtotal": str(invoice.subtotal),
        "tax": str(invoice.tax),
        "total": str(invoice.total),
        "status": invoice.status,
        "message": f"Invoice {invoice.invoice_number} created as draft for {client.display_name}.",
    }
