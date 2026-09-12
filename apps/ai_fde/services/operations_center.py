from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

from django.db.models import F, Q
from django.utils import timezone

from apps.ai_fde.services.alerts import AlertEngine

if TYPE_CHECKING:
    from apps.studios.models import Studio

logger = logging.getLogger(__name__)


class OperationsCenter:
    """Aggregated operations dashboard for a studio.

    Pulls data from multiple apps and returns a single structured dict
    suitable for the AI assistant or a dashboard view.
    """

    def get_dashboard(self, studio: Studio) -> dict[str, Any]:
        """Return the full operations-center snapshot."""
        return {
            "studio_id": str(studio.id),
            "generated_at": timezone.now().isoformat(),
            "overdue_projects": self._overdue_projects(studio),
            "outstanding_payments": self._outstanding_payments(studio),
            "awaiting_selection": self._awaiting_selection(studio),
            "editing_backlog": self._editing_backlog(studio),
            "printing_delays": self._printing_delays(studio),
            "low_inventory": self._low_inventory(studio),
            "equipment_maintenance": self._equipment_maintenance(studio),
            "upcoming_bookings": self._upcoming_bookings(studio),
            "alerts": AlertEngine().get_all_alerts(studio),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _overdue_projects(self, studio: Studio) -> dict[str, Any]:
        from apps.projects.models import Project

        today = date.today()
        projects = list(
            Project.objects.filter(
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
            )
            .select_related("client")
            .order_by("expected_delivery")
        )
        return {
            "count": len(projects),
            "items": [
                {
                    "id": str(p.id),
                    "reference": p.reference,
                    "client": p.client.display_name,
                    "status": p.status,
                    "priority": p.priority,
                    "expected_delivery": (
                        p.expected_delivery.isoformat() if p.expected_delivery else None
                    ),
                    "days_overdue": (today - p.expected_delivery).days if p.expected_delivery else 0,
                }
                for p in projects
            ],
        }

    def _outstanding_payments(self, studio: Studio) -> dict[str, Any]:
        from apps.finance.models import Invoice

        invoices = list(
            Invoice.objects.filter(
                studio=studio,
                status__in=[
                    Invoice.Status.ISSUED,
                    Invoice.Status.PARTIAL,
                    Invoice.Status.OVERDUE,
                ],
            )
            .select_related("client")
            .order_by("due_date")
        )
        total_balance = sum(inv.balance for inv in invoices)
        return {
            "count": len(invoices),
            "total_balance": float(total_balance),
            "items": [
                {
                    "id": str(inv.id),
                    "invoice_number": inv.invoice_number,
                    "client": inv.client.display_name,
                    "total": float(inv.total),
                    "amount_paid": float(inv.amount_paid),
                    "balance": float(inv.balance),
                    "status": inv.status,
                    "due_date": inv.due_date.isoformat() if inv.due_date else None,
                }
                for inv in invoices
            ],
        }

    def _awaiting_selection(self, studio: Studio) -> dict[str, Any]:
        from apps.projects.models import Project

        projects = list(
            Project.objects.filter(
                studio=studio,
                status=Project.Status.AWAITING_SELECTION,
            )
            .select_related("client")
            .order_by("created_at")
        )
        return {
            "count": len(projects),
            "items": [
                {
                    "id": str(p.id),
                    "reference": p.reference,
                    "client": p.client.display_name,
                    "shoot_date": p.shoot_date.isoformat() if p.shoot_date else None,
                    "total_for_selection": p.total_for_selection,
                }
                for p in projects
            ],
        }

    def _editing_backlog(self, studio: Studio) -> dict[str, Any]:
        from apps.projects.models import Project

        projects = list(
            Project.objects.filter(
                studio=studio,
                status__in=[
                    Project.Status.EDITING,
                    Project.Status.EDITING_REVIEW,
                ],
            )
            .select_related("client", "editor")
            .order_by("expected_delivery")
        )
        return {
            "count": len(projects),
            "items": [
                {
                    "id": str(p.id),
                    "reference": p.reference,
                    "client": p.client.display_name,
                    "status": p.status,
                    "editor": p.editor.get_full_name() if p.editor else None,
                    "expected_delivery": (
                        p.expected_delivery.isoformat() if p.expected_delivery else None
                    ),
                    "total_captured": p.total_captured,
                    "edited_count": p.edited_count,
                }
                for p in projects
            ],
        }

    def _printing_delays(self, studio: Studio) -> dict[str, Any]:
        from apps.printing.models import AlbumOrder, FrameOrder, PrintJob

        today = date.today()

        overdue_prints = list(
            PrintJob.objects.filter(
                project__studio=studio,
                due_date__lt=today,
                status__in=[
                    PrintJob.Status.PENDING,
                    PrintJob.Status.PREPARING,
                    PrintJob.Status.SENT,
                    PrintJob.Status.PRINTING,
                ],
            )
            .select_related("client", "project")
        )

        overdue_frames = list(
            FrameOrder.objects.filter(
                project__studio=studio,
                due_date__lt=today,
                status__in=[
                    FrameOrder.Status.PENDING,
                    FrameOrder.Status.ORDERED,
                ],
            )
            .select_related("project")
        )

        overdue_albums = list(
            AlbumOrder.objects.filter(
                project__studio=studio,
                delivery_date__lt=today,
                design_status__in=[
                    AlbumOrder.Status.PENDING,
                    AlbumOrder.Status.DESIGNING,
                    AlbumOrder.Status.REVIEW,
                    AlbumOrder.Status.CLIENT_APPROVAL,
                    AlbumOrder.Status.PRODUCTION,
                ],
            )
            .select_related("project")
        )

        return {
            "count": len(overdue_prints) + len(overdue_frames) + len(overdue_albums),
            "prints": [
                {
                    "id": str(p.id),
                    "client": p.client.display_name,
                    "project_reference": p.project.reference,
                    "print_size": p.print_size,
                    "quantity": p.quantity,
                    "status": p.status,
                    "due_date": p.due_date.isoformat() if p.due_date else None,
                }
                for p in overdue_prints
            ],
            "frames": [
                {
                    "id": str(f.id),
                    "project_reference": f.project.reference,
                    "size": f.size,
                    "frame_type": f.frame_type,
                    "status": f.status,
                    "due_date": f.due_date.isoformat() if f.due_date else None,
                }
                for f in overdue_frames
            ],
            "albums": [
                {
                    "id": str(a.id),
                    "project_reference": a.project.reference,
                    "album_type": a.album_type,
                    "size": a.size,
                    "design_status": a.design_status,
                    "delivery_date": a.delivery_date.isoformat() if a.delivery_date else None,
                }
                for a in overdue_albums
            ],
        }

    def _low_inventory(self, studio: Studio) -> dict[str, Any]:
        from apps.inventory.models import InventoryItem

        items = list(
            InventoryItem.objects.filter(
                studio=studio,
                is_active=True,
            )
            .filter(Q(quantity__lte=F("reorder_level")))
            .order_by("quantity")
        )
        return {
            "count": len(items),
            "items": [
                {
                    "id": str(item.id),
                    "sku": item.sku,
                    "name": item.name,
                    "category": item.category,
                    "quantity": item.quantity,
                    "reorder_level": item.reorder_level,
                    "unit": item.unit,
                    "supplier": item.supplier,
                }
                for item in items
            ],
        }

    def _equipment_maintenance(self, studio: Studio) -> dict[str, Any]:
        from apps.equipment.models import Equipment

        today = date.today()
        equipment = list(
            Equipment.objects.filter(
                studio=studio,
                next_maintenance__isnull=False,
                next_maintenance__lt=today,
            )
            .exclude(status=Equipment.Status.RETIRED)
            .order_by("next_maintenance")
        )
        return {
            "count": len(equipment),
            "items": [
                {
                    "id": str(eq.id),
                    "asset_number": eq.asset_number,
                    "name": eq.name,
                    "status": eq.status,
                    "next_maintenance": eq.next_maintenance.isoformat(),
                    "days_overdue": (today - eq.next_maintenance).days,
                }
                for eq in equipment
            ],
        }

    def _upcoming_bookings(self, studio: Studio) -> dict[str, Any]:
        from apps.bookings.models import Booking

        today = date.today()
        horizon = today + timedelta(days=14)

        bookings = list(
            Booking.objects.filter(
                studio=studio,
                date__gte=today,
                date__lte=horizon,
                status__in=[
                    Booking.Status.CONFIRMED,
                    Booking.Status.IN_PROGRESS,
                ],
            )
            .select_related("client", "package", "photographer")
            .order_by("date", "start_time")
        )

        unassigned = [b for b in bookings if b.photographer is None]

        return {
            "count": len(bookings),
            "unassigned_count": len(unassigned),
            "items": [
                {
                    "id": str(b.id),
                    "reference": b.reference,
                    "client": b.client.display_name,
                    "event_type": b.event_type,
                    "date": b.date.isoformat(),
                    "start_time": b.start_time.isoformat() if b.start_time else None,
                    "photographer": (
                        b.photographer.get_full_name() if b.photographer else None
                    ),
                    "status": b.status,
                    "total_amount": float(b.total_amount),
                }
                for b in bookings
            ],
        }
