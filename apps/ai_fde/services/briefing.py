from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from django.db.models import F, Q, Sum

if TYPE_CHECKING:
    from apps.studios.models import Studio

logger = logging.getLogger(__name__)


def generate_briefing_data(studio: Studio) -> dict[str, Any]:
    """Generate structured data for the morning briefing.

    Pure Django ORM queries — no LLM calls.  Includes deterministic
    alerts from :class:`AlertEngine`.

    Args:
        studio: The studio to generate the briefing for.

    Returns:
        A dict containing all briefing metrics and alerts.
    """
    from apps.bookings.models import Booking
    from apps.finance.models import Invoice
    from apps.inventory.models import InventoryItem
    from apps.projects.models import Project

    today = date.today()

    # ── Bookings today ──────────────────────────────────────────────
    bookings_today = Booking.objects.filter(
        studio=studio,
        date=today,
        status__in=[
            Booking.Status.CONFIRMED,
            Booking.Status.IN_PROGRESS,
        ],
    ).select_related("client", "package").order_by("start_time")

    # ── Projects ────────────────────────────────────────────────────
    overdue_projects = Project.objects.filter(
        studio=studio,
        expected_delivery__lt=today,
        status__in=[
            Project.Status.SCHEDULED,
            Project.Status.SHOOT_COMPLETED,
            Project.Status.FILES_IMPORTED,
            Project.Status.AWAITING_SELECTION,
            Project.Status.SELECTION_RECEIVED,
            Project.Status.EDITING,
            Project.Status.EDITING_REVIEW,
            Project.Status.READY_FOR_PRINT,
            Project.Status.PRINTING,
            Project.Status.QUALITY_CONTROL,
        ],
    ).select_related("client").order_by("expected_delivery")

    awaiting_selection = Project.objects.filter(
        studio=studio,
        status=Project.Status.AWAITING_SELECTION,
    ).select_related("client")

    editing_count = Project.objects.filter(
        studio=studio,
        status__in=[
            Project.Status.EDITING,
            Project.Status.EDITING_REVIEW,
        ],
    ).count()

    ready_for_delivery = Project.objects.filter(
        studio=studio,
        status=Project.Status.READY_FOR_DELIVERY,
    ).select_related("client")

    # ── Finance ─────────────────────────────────────────────────────
    outstanding_invoices = Invoice.objects.filter(
        studio=studio,
        status__in=[Invoice.Status.ISSUED, Invoice.Status.PARTIAL, Invoice.Status.OVERDUE],
    )
    outstanding_amount = outstanding_invoices.aggregate(
        total=Sum("balance")
    )["total"] or Decimal("0.00")

    payments_expected = Invoice.objects.filter(
        studio=studio,
        status=Invoice.Status.PARTIAL,
    ).aggregate(total=Sum("balance"))["total"] or Decimal("0.00")

    # ── Inventory ───────────────────────────────────────────────────
    low_stock_count = InventoryItem.objects.filter(
        studio=studio,
        is_active=True,
    ).filter(
        Q(quantity__lte=F("reorder_level"))
    ).count()

    # ── Alerts ──────────────────────────────────────────────────────
    from apps.ai_fde.services.alerts import AlertEngine

    alert_engine = AlertEngine()
    alerts = alert_engine.get_all_alerts(studio)

    # ── Summary stats ───────────────────────────────────────────────
    total_bookings_today = bookings_today.count()
    total_overdue = overdue_projects.count()
    total_awaiting = awaiting_selection.count()
    total_ready = ready_for_delivery.count()
    total_alerts = len(alerts)
    error_count = sum(1 for a in alerts if a.get("severity") == "error")
    warning_count = sum(1 for a in alerts if a.get("severity") == "warning")

    return {
        "date": today.isoformat(),
        "summary": {
            "bookings_today": total_bookings_today,
            "overdue_projects": total_overdue,
            "awaiting_selection": total_awaiting,
            "editing": editing_count,
            "ready_for_delivery": total_ready,
            "outstanding_amount": float(outstanding_amount),
            "payments_expected": float(payments_expected),
            "low_stock_items": low_stock_count,
            "total_alerts": total_alerts,
            "error_alerts": error_count,
            "warning_alerts": warning_count,
        },
        "bookings_today": [
            {
                "id": str(b.id),
                "reference": b.reference,
                "client": b.client.display_name,
                "event_type": b.event_type,
                "time": b.start_time.strftime("%H:%M") if b.start_time else None,
                "status": b.status,
            }
            for b in bookings_today
        ],
        "overdue_projects": [
            {
                "id": str(p.id),
                "reference": p.reference,
                "client": p.client.display_name,
                "status": p.status,
                "expected_delivery": (
                    p.expected_delivery.isoformat() if p.expected_delivery else None
                ),
                "priority": p.priority,
            }
            for p in overdue_projects
        ],
        "awaiting_selection": [
            {
                "id": str(p.id),
                "reference": p.reference,
                "client": p.client.display_name,
            }
            for p in awaiting_selection
        ],
        "editing_count": editing_count,
        "ready_for_delivery": [
            {
                "id": str(p.id),
                "reference": p.reference,
                "client": p.client.display_name,
            }
            for p in ready_for_delivery
        ],
        "outstanding_amount": float(outstanding_amount),
        "payments_expected": float(payments_expected),
        "low_stock_count": low_stock_count,
        "alerts": alerts,
    }
