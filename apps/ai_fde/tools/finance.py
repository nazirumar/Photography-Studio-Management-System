from __future__ import annotations

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from django.db.models import Q, Sum

from apps.expenses.models import Expense
from apps.finance.models import Invoice, Payment

from .base import FDEContext, fde_tool

logger = logging.getLogger(__name__)

_PERIOD_DELTAS: dict[str, int] = {
    "week": 7,
    "month": 30,
    "quarter": 90,
    "year": 365,
}


def _resolve_period(period: str) -> tuple[date, date]:
    today = date.today()
    days = _PERIOD_DELTAS.get(period)
    if days is None:
        days = 30
    return today - timedelta(days=days), today


def _invoice_to_dict(inv: Invoice) -> dict[str, Any]:
    return {
        "id": str(inv.id),
        "invoice_number": inv.invoice_number,
        "client": str(inv.client),
        "client_id": str(inv.client_id) if inv.client_id else None,
        "issue_date": inv.issue_date.isoformat(),
        "due_date": inv.due_date.isoformat() if inv.due_date else None,
        "subtotal": float(inv.subtotal),
        "discount": float(inv.discount),
        "tax": float(inv.tax),
        "total": float(inv.total),
        "amount_paid": float(inv.amount_paid),
        "balance": float(inv.balance),
        "status": inv.status,
    }


def _payment_to_dict(p: Payment) -> dict[str, Any]:
    return {
        "id": str(p.id),
        "reference": p.reference,
        "client": str(p.client),
        "client_id": str(p.client_id) if p.client_id else None,
        "invoice_id": str(p.invoice_id) if p.invoice_id else None,
        "amount": float(p.amount),
        "payment_date": p.payment_date.isoformat(),
        "method": p.method,
        "notes": p.notes,
    }


@fde_tool(
    name="get_invoice",
    permission="finance.view_invoice",
    risk="read",
    description="Get a single invoice by ID.",
    timeout=15,
)
def get_invoice(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        invoice_id = params.get("invoice_id", "").strip()
        if not invoice_id:
            return {"success": False, "error": "invoice_id is required."}

        inv = Invoice.objects.select_related("client", "booking").get(
            id=invoice_id, studio=context.studio
        )
        return {"success": True, "invoice": _invoice_to_dict(inv)}
    except Invoice.DoesNotExist:
        return {"success": False, "error": "Invoice not found."}
    except Exception as exc:
        logger.exception("Error getting invoice %s", params.get("invoice_id"))
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="search_invoices",
    permission="finance.view_invoice",
    risk="read",
    description="Search invoices by number or client name, optionally filtered by status.",
    timeout=15,
)
def search_invoices(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        query = params.get("query", "").strip()
        status = params.get("status", "").strip()
        limit = int(params.get("limit", 10))

        qs = Invoice.objects.filter(studio=context.studio).select_related("client")

        if status:
            qs = qs.filter(status=status)

        if query:
            qs = qs.filter(
                Q(invoice_number__icontains=query)
                | Q(client__first_name__icontains=query)
                | Q(client__last_name__icontains=query)
                | Q(client__display_name__icontains=query)
            )

        invoices = list(qs[:limit])
        return {
            "success": True,
            "count": len(invoices),
            "invoices": [_invoice_to_dict(i) for i in invoices],
        }
    except Exception as exc:
        logger.exception("Error searching invoices")
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="get_outstanding_invoices",
    permission="finance.view_invoice",
    risk="read",
    description="Get all unpaid or partially-paid invoices.",
    timeout=15,
)
def get_outstanding_invoices(
    context: FDEContext, params: dict[str, Any]
) -> dict[str, Any]:
    try:
        invoices = list(
            Invoice.objects.filter(studio=context.studio)
            .exclude(status__in=["paid", "cancelled"])
            .select_related("client")
            .order_by("due_date")
        )

        total_outstanding = sum(i.balance for i in invoices)

        return {
            "success": True,
            "count": len(invoices),
            "total_outstanding": float(total_outstanding),
            "invoices": [_invoice_to_dict(i) for i in invoices],
        }
    except Exception as exc:
        logger.exception("Error getting outstanding invoices")
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="get_revenue_summary",
    permission="finance.view_invoice",
    risk="read",
    description="Revenue summary for a given period (week/month/quarter/year).",
    timeout=15,
)
def get_revenue_summary(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        period = params.get("period", "month")
        start, end = _resolve_period(period)

        payments = Payment.objects.filter(
            studio=context.studio,
            payment_date__gte=start,
            payment_date__lte=end,
        )
        total = payments.aggregate(t=Sum("amount"))["t"] or Decimal("0")
        count = payments.count()

        return {
            "success": True,
            "period": period,
            "from": start.isoformat(),
            "to": end.isoformat(),
            "total_revenue": float(total),
            "payment_count": count,
        }
    except Exception as exc:
        logger.exception("Error getting revenue summary")
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="get_expense_summary",
    permission="expenses.view_expense",
    risk="read",
    description="Expense summary for a given period (week/month/quarter/year).",
    timeout=15,
)
def get_expense_summary(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        period = params.get("period", "month")
        start, end = _resolve_period(period)

        expenses = Expense.objects.filter(
            studio=context.studio,
            date__gte=start,
            date__lte=end,
        )
        total = expenses.aggregate(t=Sum("amount"))["t"] or Decimal("0")
        count = expenses.count()

        by_category: list[dict[str, Any]] = []

        cat_agg = (
            expenses.values("category__name")
            .annotate(cat_total=Sum("amount"))
            .order_by("-cat_total")
        )
        for row in cat_agg:
            by_category.append(
                {
                    "category": row["category__name"] or "Uncategorized",
                    "total": float(row["cat_total"]),
                }
            )

        return {
            "success": True,
            "period": period,
            "from": start.isoformat(),
            "to": end.isoformat(),
            "total_expenses": float(total),
            "expense_count": count,
            "by_category": by_category,
        }
    except Exception as exc:
        logger.exception("Error getting expense summary")
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="get_profit_summary",
    permission="finance.view_invoice",
    risk="read",
    description="Profit summary (revenue minus expenses) for a given period.",
    timeout=15,
)
def get_profit_summary(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        period = params.get("period", "month")
        start, end = _resolve_period(period)

        revenue = (
            Payment.objects.filter(
                studio=context.studio,
                payment_date__gte=start,
                payment_date__lte=end,
            ).aggregate(t=Sum("amount"))["t"]
            or Decimal("0")
        )

        expenses_total = (
            Expense.objects.filter(
                studio=context.studio,
                date__gte=start,
                date__lte=end,
            ).aggregate(t=Sum("amount"))["t"]
            or Decimal("0")
        )

        profit = revenue - expenses_total

        return {
            "success": True,
            "period": period,
            "from": start.isoformat(),
            "to": end.isoformat(),
            "revenue": float(revenue),
            "expenses": float(expenses_total),
            "profit": float(profit),
        }
    except Exception as exc:
        logger.exception("Error getting profit summary")
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="get_payment_summary",
    permission="finance.view_payment",
    risk="read",
    description="List recent payments.",
    timeout=15,
)
def get_payment_summary(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        limit = int(params.get("limit", 10))

        payments = list(
            Payment.objects.filter(studio=context.studio)
            .select_related("client")
            .order_by("-payment_date")[:limit]
        )

        total = sum(p.amount for p in payments)

        return {
            "success": True,
            "count": len(payments),
            "total_displayed": float(total),
            "payments": [_payment_to_dict(p) for p in payments],
        }
    except Exception as exc:
        logger.exception("Error getting payment summary")
        return {"success": False, "error": str(exc)}
