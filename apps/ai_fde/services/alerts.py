from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

from django.db.models import F, Q

if TYPE_CHECKING:
    from apps.studios.models import Studio

logger = logging.getLogger(__name__)


class AlertEngine:
    """Deterministic alert engine — returns structured alerts for the studio dashboard.

    Each alert is a dict with keys:
        - type: short machine-readable label
        - severity: info | warning | error
        - message: human-readable description
        - entity_type: model name (e.g. "project", "invoice")
        - entity_id: str(uuid) of the related object
        - details: dict of extra context
    """

    def get_all_alerts(self, studio: Studio) -> list[dict[str, Any]]:
        """Aggregate every active alert category for *studio*."""
        alerts: list[dict[str, Any]] = []
        alerts.extend(self.overdue_projects(studio))
        alerts.extend(self.due_soon_projects(studio))
        alerts.extend(self.outstanding_invoices(studio))
        alerts.extend(self.low_stock(studio))
        alerts.extend(self.equipment_maintenance(studio))
        alerts.extend(self.bookings_without_photographer(studio))
        return alerts

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    def overdue_projects(self, studio: Studio) -> list[dict[str, Any]]:
        """Projects past ``expected_delivery`` that are not completed."""
        from apps.projects.models import Project

        today = date.today()
        projects = Project.objects.filter(
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
        ).select_related("client")

        return [
            {
                "type": "overdue_project",
                "severity": "error",
                "message": (
                    f"Project {p.reference} ({p.client.display_name}) "
                    f"overdue by {(today - p.expected_delivery).days} days"
                ),
                "entity_type": "project",
                "entity_id": str(p.id),
                "details": {
                    "reference": p.reference,
                    "client": p.client.display_name,
                    "status": p.status,
                    "expected_delivery": p.expected_delivery.isoformat(),
                    "days_overdue": (today - p.expected_delivery).days,
                },
            }
            for p in projects
        ]

    def due_soon_projects(self, studio: Studio) -> list[dict[str, Any]]:
        """Projects due within 3 days still in editing stages."""
        from apps.projects.models import Project

        today = date.today()
        horizon = today + timedelta(days=3)

        projects = Project.objects.filter(
            studio=studio,
            expected_delivery__gte=today,
            expected_delivery__lte=horizon,
            status__in=[
                Project.Status.EDITING,
                Project.Status.EDITING_REVIEW,
                Project.Status.FILES_IMPORTED,
                Project.Status.SELECTION_RECEIVED,
            ],
        ).select_related("client")

        return [
            {
                "type": "due_soon_project",
                "severity": "warning",
                "message": (
                    f"Project {p.reference} ({p.client.display_name}) "
                    f"due {p.expected_delivery.isoformat()} — still in {p.get_status_display()}"
                ),
                "entity_type": "project",
                "entity_id": str(p.id),
                "details": {
                    "reference": p.reference,
                    "client": p.client.display_name,
                    "status": p.status,
                    "expected_delivery": p.expected_delivery.isoformat(),
                    "days_remaining": (p.expected_delivery - today).days,
                },
            }
            for p in projects
        ]

    # ------------------------------------------------------------------
    # Finance
    # ------------------------------------------------------------------

    def outstanding_invoices(self, studio: Studio) -> list[dict[str, Any]]:
        """Invoices with status issued, partial, or overdue."""
        from apps.finance.models import Invoice

        invoices = Invoice.objects.filter(
            studio=studio,
            status__in=[
                Invoice.Status.ISSUED,
                Invoice.Status.PARTIAL,
                Invoice.Status.OVERDUE,
            ],
        ).select_related("client")

        today = date.today()

        return [
            {
                "type": "outstanding_invoice",
                "severity": "error" if inv.status == Invoice.Status.OVERDUE else "warning",
                "message": (
                    f"Invoice {inv.invoice_number} ({inv.client.display_name}) — "
                    f"₦{inv.balance:,.2f} balance"
                    + (
                        f", {inv.due_date.isoformat()}"
                        if inv.due_date
                        else ""
                    )
                ),
                "entity_type": "invoice",
                "entity_id": str(inv.id),
                "details": {
                    "invoice_number": inv.invoice_number,
                    "client": inv.client.display_name,
                    "total": float(inv.total),
                    "amount_paid": float(inv.amount_paid),
                    "balance": float(inv.balance),
                    "status": inv.status,
                    "due_date": inv.due_date.isoformat() if inv.due_date else None,
                    "is_overdue": bool(inv.due_date and inv.due_date < today),
                },
            }
            for inv in invoices
        ]

    # ------------------------------------------------------------------
    # Inventory
    # ------------------------------------------------------------------

    def low_stock(self, studio: Studio) -> list[dict[str, Any]]:
        """Active inventory items at or below ``reorder_level``."""
        from apps.inventory.models import InventoryItem

        items = InventoryItem.objects.filter(
            studio=studio,
            is_active=True,
        ).filter(Q(quantity__lte=F("reorder_level")))

        return [
            {
                "type": "low_stock",
                "severity": "warning",
                "message": (
                    f"{item.name} ({item.sku}) — {item.quantity} {item.unit} remaining "
                    f"(reorder at {item.reorder_level})"
                ),
                "entity_type": "inventory_item",
                "entity_id": str(item.id),
                "details": {
                    "sku": item.sku,
                    "name": item.name,
                    "quantity": item.quantity,
                    "reorder_level": item.reorder_level,
                    "category": item.category,
                },
            }
            for item in items
        ]

    # ------------------------------------------------------------------
    # Equipment
    # ------------------------------------------------------------------

    def equipment_maintenance(self, studio: Studio) -> list[dict[str, Any]]:
        """Equipment with ``next_maintenance`` in the past or missing."""
        from apps.equipment.models import Equipment

        today = date.today()
        equipment = Equipment.objects.filter(
            studio=studio,
            next_maintenance__isnull=False,
            next_maintenance__lt=today,
        ).exclude(status=Equipment.Status.RETIRED)

        return [
            {
                "type": "equipment_maintenance",
                "severity": "warning",
                "message": (
                    f"{eq.name} ({eq.asset_number}) — maintenance was due "
                    f"{eq.next_maintenance.isoformat()}"
                ),
                "entity_type": "equipment",
                "entity_id": str(eq.id),
                "details": {
                    "asset_number": eq.asset_number,
                    "name": eq.name,
                    "status": eq.status,
                    "next_maintenance": eq.next_maintenance.isoformat(),
                    "days_overdue": (today - eq.next_maintenance).days,
                },
            }
            for eq in equipment
        ]

    # ------------------------------------------------------------------
    # Bookings
    # ------------------------------------------------------------------

    def bookings_without_photographer(self, studio: Studio) -> list[dict[str, Any]]:
        """Confirmed bookings in the next 7 days with no photographer assigned."""
        from apps.bookings.models import Booking

        today = date.today()
        horizon = today + timedelta(days=7)

        bookings = Booking.objects.filter(
            studio=studio,
            date__gte=today,
            date__lte=horizon,
            status__in=[Booking.Status.CONFIRMED, Booking.Status.IN_PROGRESS],
            photographer__isnull=True,
        ).select_related("client")

        return [
            {
                "type": "unassigned_booking",
                "severity": "error",
                "message": (
                    f"Booking {b.reference} ({b.client.display_name}) "
                    f"on {b.date.isoformat()} — no photographer assigned"
                ),
                "entity_type": "booking",
                "entity_id": str(b.id),
                "details": {
                    "reference": b.reference,
                    "client": b.client.display_name,
                    "date": b.date.isoformat(),
                    "start_time": b.start_time.isoformat() if b.start_time else None,
                    "event_type": b.event_type,
                    "status": b.status,
                },
            }
            for b in bookings
        ]
