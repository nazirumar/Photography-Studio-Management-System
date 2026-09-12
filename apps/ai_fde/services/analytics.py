from __future__ import annotations

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from django.db.models import Avg, Count, F, Sum

if TYPE_CHECKING:
    from apps.studios.models import Studio

logger = logging.getLogger(__name__)

PERIOD_MAP = {
    "week": timedelta(weeks=1),
    "month": timedelta(days=30),
    "quarter": timedelta(days=90),
    "year": timedelta(days=365),
}


def _period_start(period: str) -> date:
    """Calculate the start date for a given period string."""
    delta = PERIOD_MAP.get(period, timedelta(days=30))
    return date.today() - delta


def get_revenue_summary(studio: Studio, period: str = "month") -> dict[str, Any]:
    """Return revenue metrics for the specified period.

    Args:
        studio: The studio to query.
        period: One of 'week', 'month', 'quarter', 'year'.

    Returns:
        Dict with total_revenue, payment_count, average_payment, and by_method breakdown.
    """
    from apps.finance.models import Payment

    start = _period_start(period)
    payments = Payment.objects.filter(
        studio=studio,
        payment_date__gte=start,
    )

    agg = payments.aggregate(
        total_revenue=Sum("amount"),
        payment_count=Count("id"),
        average_payment=Avg("amount"),
    )

    by_method = (
        payments.values("method")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("-total")
    )

    return {
        "period": period,
        "start_date": start.isoformat(),
        "total_revenue": float(agg["total_revenue"] or Decimal("0.00")),
        "payment_count": agg["payment_count"] or 0,
        "average_payment": float(agg["average_payment"] or Decimal("0.00")),
        "by_method": [
            {
                "method": row["method"],
                "total": float(row["total"]),
                "count": row["count"],
            }
            for row in by_method
        ],
    }


def get_expense_summary(studio: Studio, period: str = "month") -> dict[str, Any]:
    """Return expense metrics for the specified period.

    Args:
        studio: The studio to query.
        period: One of 'week', 'month', 'quarter', 'year'.

    Returns:
        Dict with total_expenses, expense_count, and by_category breakdown.
    """
    from apps.expenses.models import Expense

    start = _period_start(period)
    expenses = Expense.objects.filter(
        studio=studio,
        date__gte=start,
    )

    agg = expenses.aggregate(
        total_expenses=Sum("amount"),
        expense_count=Count("id"),
    )

    by_category = (
        expenses.values("category__name")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("-total")
    )

    return {
        "period": period,
        "start_date": start.isoformat(),
        "total_expenses": float(agg["total_expenses"] or Decimal("0.00")),
        "expense_count": agg["expense_count"] or 0,
        "by_category": [
            {
                "category": row["category__name"] or "Uncategorized",
                "total": float(row["total"]),
                "count": row["count"],
            }
            for row in by_category
        ],
    }


def get_profit_summary(studio: Studio, period: str = "month") -> dict[str, Any]:
    """Return profit (revenue minus expenses) for the specified period.

    Args:
        studio: The studio to query.
        period: One of 'week', 'month', 'quarter', 'year'.

    Returns:
        Dict with revenue, expenses, profit, and margin percentage.
    """
    revenue_data = get_revenue_summary(studio, period)
    expense_data = get_expense_summary(studio, period)

    total_revenue = revenue_data["total_revenue"]
    total_expenses = expense_data["total_expenses"]
    profit = total_revenue - total_expenses
    margin = (profit / total_revenue * 100) if total_revenue else 0.0

    return {
        "period": period,
        "start_date": revenue_data["start_date"],
        "revenue": total_revenue,
        "expenses": total_expenses,
        "profit": profit,
        "margin_pct": round(margin, 1),
    }


def get_package_performance(studio: Studio) -> list[dict[str, Any]]:
    """Return booking performance metrics per package.

    Args:
        studio: The studio to query.

    Returns:
        A list of dicts sorted by total revenue descending.
    """
    from apps.bookings.models import Booking

    packages = (
        Booking.objects.filter(
            studio=studio,
            status__in=[Booking.Status.CONFIRMED, Booking.Status.COMPLETED],
        )
        .values("package__name")
        .annotate(
            booking_count=Count("id"),
            total_revenue=Sum("total_amount"),
            average_amount=Avg("total_amount"),
        )
        .order_by("-total_revenue")
    )

    return [
        {
            "package": row["package__name"] or "No Package",
            "booking_count": row["booking_count"],
            "total_revenue": float(row["total_revenue"] or Decimal("0.00")),
            "average_amount": float(row["average_amount"] or Decimal("0.00")),
        }
        for row in packages
    ]


def get_project_turnaround(studio: Studio) -> dict[str, Any]:
    """Return project turnaround metrics.

    Args:
        studio: The studio to query.

    Returns:
        Dict with average_days, median_days, and by_status breakdown for
        completed projects.
    """
    from apps.projects.models import Project

    completed = Project.objects.filter(
        studio=studio,
        status=Project.Status.COMPLETED,
        shoot_date__isnull=False,
        actual_delivery__isnull=False,
    )

    turnaround_data = []
    for project in completed.only("shoot_date", "actual_delivery", "status"):
        days = (project.actual_delivery - project.shoot_date).days
        turnaround_data.append(days)

    avg_days = (
        sum(turnaround_data) / len(turnaround_data) if turnaround_data else 0
    )
    sorted_days = sorted(turnaround_data)
    mid = len(sorted_days) // 2
    median_days = (
        sorted_days[mid]
        if len(sorted_days) % 2
        else (sorted_days[mid - 1] + sorted_days[mid]) / 2
        if sorted_days
        else 0
    )

    by_priority = (
        completed.values("priority")
        .annotate(avg_turnaround=Avg(
            F("actual_delivery") - F("shoot_date")
        ))
        .order_by("priority")
    )

    return {
        "total_completed": completed.count(),
        "average_days": round(avg_days, 1),
        "median_days": round(median_days, 1),
        "by_priority": [
            {
                "priority": row["priority"],
                "avg_days": round(row["avg_turnaround"].days if row["avg_turnaround"] else 0, 1),
            }
            for row in by_priority
        ],
    }
