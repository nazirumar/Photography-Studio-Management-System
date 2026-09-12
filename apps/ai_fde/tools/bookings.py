from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from django.db.models import Q

from apps.bookings.models import Booking

from .base import FDEContext, fde_tool

logger = logging.getLogger(__name__)


def _booking_to_dict(b: Booking) -> dict[str, Any]:
    return {
        "id": str(b.id),
        "reference": b.reference,
        "client": str(b.client),
        "client_id": str(b.client_id) if b.client_id else None,
        "title": b.title,
        "event_type": b.event_type,
        "date": b.date.isoformat(),
        "start_time": b.start_time.isoformat() if b.start_time else None,
        "end_time": b.end_time.isoformat() if b.end_time else None,
        "location": b.location,
        "location_type": b.location_type,
        "photographer_id": str(b.photographer_id) if b.photographer_id else None,
        "status": b.status,
        "payment_status": b.payment_status,
        "total_amount": float(b.total_amount),
        "amount_paid": float(b.amount_paid),
        "balance": float(b.balance),
    }


@fde_tool(
    name="get_booking",
    permission="bookings.view_booking",
    risk="read",
    description="Get a single booking by ID.",
    timeout=15,
)
def get_booking(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        booking_id = params.get("booking_id", "").strip()
        if not booking_id:
            return {"success": False, "error": "booking_id is required."}

        booking = Booking.objects.select_related("client").get(
            id=booking_id, studio=context.studio
        )
        return {"success": True, "booking": _booking_to_dict(booking)}
    except Booking.DoesNotExist:
        return {"success": False, "error": "Booking not found."}
    except Exception as exc:
        logger.exception("Error getting booking %s", params.get("booking_id"))
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="search_bookings",
    permission="bookings.view_booking",
    risk="read",
    description="Search bookings by client name, reference, or title, optionally filtered by status.",
    timeout=15,
)
def search_bookings(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        query = params.get("query", "").strip()
        status = params.get("status", "").strip()
        limit = int(params.get("limit", 10))

        qs = Booking.objects.filter(studio=context.studio).select_related("client")

        if status:
            qs = qs.filter(status=status)

        if query:
            qs = qs.filter(
                Q(reference__icontains=query)
                | Q(title__icontains=query)
                | Q(client__first_name__icontains=query)
                | Q(client__last_name__icontains=query)
                | Q(client__display_name__icontains=query)
            )

        bookings = list(qs[:limit])
        return {
            "success": True,
            "count": len(bookings),
            "bookings": [_booking_to_dict(b) for b in bookings],
        }
    except Exception as exc:
        logger.exception("Error searching bookings")
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="get_today_bookings",
    permission="bookings.view_booking",
    risk="read",
    description="Get all bookings scheduled for today.",
    timeout=15,
)
def get_today_bookings(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        today = date.today()
        bookings = list(
            Booking.objects.filter(studio=context.studio, date=today)
            .exclude(status__in=[Booking.Status.CANCELLED, Booking.Status.NO_SHOW])
            .select_related("client")
            .order_by("start_time")
        )
        return {
            "success": True,
            "date": today.isoformat(),
            "count": len(bookings),
            "bookings": [_booking_to_dict(b) for b in bookings],
        }
    except Exception as exc:
        logger.exception("Error getting today's bookings")
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="get_upcoming_bookings",
    permission="bookings.view_booking",
    risk="read",
    description="Get bookings for the next N days (default 7).",
    timeout=15,
)
def get_upcoming_bookings(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        days = int(params.get("days", 7))
        today = date.today()
        end = today + timedelta(days=days)

        bookings = list(
            Booking.objects.filter(
                studio=context.studio, date__gte=today, date__lte=end
            )
            .exclude(status__in=[Booking.Status.CANCELLED, Booking.Status.NO_SHOW])
            .select_related("client")
            .order_by("date", "start_time")
        )
        return {
            "success": True,
            "from": today.isoformat(),
            "to": end.isoformat(),
            "count": len(bookings),
            "bookings": [_booking_to_dict(b) for b in bookings],
        }
    except Exception as exc:
        logger.exception("Error getting upcoming bookings")
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="get_booking_conflicts",
    permission="bookings.view_booking",
    risk="read",
    description="Detect booking conflicts on a given date, optionally filtered by photographer.",
    timeout=15,
)
def get_booking_conflicts(
    context: FDEContext, params: dict[str, Any]
) -> dict[str, Any]:
    try:
        date_str = params.get("date", "").strip()
        photographer_id = params.get("photographer_id", "").strip()

        if not date_str:
            return {"success": False, "error": "date parameter is required (YYYY-MM-DD)."}

        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD."}

        qs = Booking.objects.filter(studio=context.studio, date=target_date).exclude(
            status__in=[Booking.Status.CANCELLED, Booking.Status.NO_SHOW]
        )

        if photographer_id:
            qs = qs.filter(photographer_id=photographer_id)

        bookings = list(qs.order_by("start_time").select_related("client"))

        conflicts: list[dict[str, Any]] = []
        for i in range(len(bookings)):
            for j in range(i + 1, len(bookings)):
                b1, b2 = bookings[i], bookings[j]
                # Conflict if both have times and they overlap
                if (b1.start_time and b1.end_time and b2.start_time and b2.end_time
                        and b1.start_time < b2.end_time and b2.start_time < b1.end_time):
                        conflicts.append(
                            {
                                "booking_1": _booking_to_dict(b1),
                                "booking_2": _booking_to_dict(b2),
                            }
                        )

        return {
            "success": True,
            "date": target_date.isoformat(),
            "total_bookings": len(bookings),
            "conflicts_found": len(conflicts),
            "conflicts": conflicts,
        }
    except Exception as exc:
        logger.exception("Error checking booking conflicts")
        return {"success": False, "error": str(exc)}
