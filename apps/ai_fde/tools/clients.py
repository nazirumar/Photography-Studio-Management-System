from __future__ import annotations

import logging
from typing import Any

from django.db.models import Q

from apps.clients.models import Client

from .base import FDEContext, fde_tool

logger = logging.getLogger(__name__)


def _client_to_dict(client: Client) -> dict[str, Any]:
    return {
        "id": str(client.id),
        "client_number": client.client_number,
        "first_name": client.first_name,
        "last_name": client.last_name,
        "display_name": client.display_name,
        "email": client.email,
        "phone": client.phone,
        "whatsapp": client.whatsapp,
        "city": client.city,
        "state": client.state,
        "status": client.status,
        "referral_source": client.referral_source,
        "notes": client.notes,
        "created_at": client.created_at.isoformat() if client.created_at else None,
        "last_activity": client.last_activity.isoformat() if client.last_activity else None,
    }


@fde_tool(
    name="search_clients",
    permission="clients.view_client",
    risk="read",
    description="Search clients by name, email, or phone number.",
    timeout=15,
)
def search_clients(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        query = params.get("query", "").strip()
        limit = int(params.get("limit", 5))

        if not query:
            return {"success": False, "error": "Query parameter is required."}

        qs = Client.objects.filter(studio=context.studio, status="active")
        qs = qs.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(display_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
        )
        clients = list(qs[:limit])
        return {
            "success": True,
            "count": len(clients),
            "clients": [_client_to_dict(c) for c in clients],
        }
    except Exception as exc:
        logger.exception("Error searching clients")
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="get_client",
    permission="clients.view_client",
    risk="read",
    description="Get a single client by ID.",
    timeout=15,
)
def get_client(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        client_id = params.get("client_id", "").strip()
        if not client_id:
            return {"success": False, "error": "client_id is required."}

        client = Client.objects.get(id=client_id, studio=context.studio)
        return {"success": True, "client": _client_to_dict(client)}
    except Client.DoesNotExist:
        return {"success": False, "error": "Client not found."}
    except Exception as exc:
        logger.exception("Error getting client %s", params.get("client_id"))
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="get_client_history",
    permission="clients.view_client",
    risk="read",
    description="Get a client's booking and invoice history.",
    timeout=20,
)
def get_client_history(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        client_id = params.get("client_id", "").strip()
        if not client_id:
            return {"success": False, "error": "client_id is required."}

        client = Client.objects.get(id=client_id, studio=context.studio)

        from apps.bookings.models import Booking
        from apps.finance.models import Invoice

        bookings = Booking.objects.filter(client=client, studio=context.studio).order_by(
            "-date"
        )[:20]
        invoices = Invoice.objects.filter(client=client, studio=context.studio).order_by(
            "-issue_date"
        )[:20]

        return {
            "success": True,
            "client": _client_to_dict(client),
            "bookings": [
                {
                    "id": str(b.id),
                    "reference": b.reference,
                    "date": b.date.isoformat(),
                    "status": b.status,
                    "payment_status": b.payment_status,
                    "total_amount": float(b.total_amount),
                    "balance": float(b.balance),
                }
                for b in bookings
            ],
            "invoices": [
                {
                    "id": str(inv.id),
                    "invoice_number": inv.invoice_number,
                    "issue_date": inv.issue_date.isoformat(),
                    "due_date": inv.due_date.isoformat() if inv.due_date else None,
                    "total": float(inv.total),
                    "amount_paid": float(inv.amount_paid),
                    "balance": float(inv.balance),
                    "status": inv.status,
                }
                for inv in invoices
            ],
        }
    except Client.DoesNotExist:
        return {"success": False, "error": "Client not found."}
    except Exception as exc:
        logger.exception("Error getting client history for %s", params.get("client_id"))
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="get_client_balance",
    permission="clients.view_client",
    risk="read",
    description="Get the outstanding balance across all unpaid invoices for a client.",
    timeout=15,
)
def get_client_balance(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        client_id = params.get("client_id", "").strip()
        if not client_id:
            return {"success": False, "error": "client_id is required."}

        client = Client.objects.get(id=client_id, studio=context.studio)

        from django.db.models import Sum

        from apps.finance.models import Invoice

        agg = Invoice.objects.filter(
            client=client, studio=context.studio
        ).exclude(status__in=["paid", "cancelled"]).aggregate(
            total_due=Sum("balance")
        )
        total_due = agg["total_due"] or 0

        return {
            "success": True,
            "client": _client_to_dict(client),
            "outstanding_balance": float(total_due),
        }
    except Client.DoesNotExist:
        return {"success": False, "error": "Client not found."}
    except Exception as exc:
        logger.exception("Error getting client balance for %s", params.get("client_id"))
        return {"success": False, "error": str(exc)}
