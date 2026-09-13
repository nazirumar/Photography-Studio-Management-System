from datetime import date, timedelta
from decimal import Decimal
from collections import defaultdict

from django.db.models import Sum, Avg, Count
from apps.finance.models import Payment, Invoice


def get_revenue_forecast(studio, months=6):
    """Simple revenue forecasting based on historical data."""
    today = date.today()

    # Get monthly revenue for last 12 months
    monthly_revenue = []
    for i in range(12, 0, -1):
        month_start = (today - timedelta(days=30 * i)).replace(day=1)
        if i == 1:
            month_end = today
        else:
            month_end = (today - timedelta(days=30 * (i - 1))).replace(day=1) - timedelta(days=1)

        total = Payment.objects.filter(
            studio=studio,
            payment_date__gte=month_start,
            payment_date__lte=month_end,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        monthly_revenue.append({
            "month": month_start.strftime("%b %Y"),
            "revenue": float(total),
        })

    # Calculate moving average
    if len(monthly_revenue) >= 3:
        recent_3 = [m["revenue"] for m in monthly_revenue[-3:]]
        avg_revenue = sum(recent_3) / 3
        growth_rate = 0
        if len(monthly_revenue) >= 6:
            older_3 = [m["revenue"] for m in monthly_revenue[-6:-3]]
            older_avg = sum(older_3) / 3 if older_3 else 1
            if older_avg > 0:
                growth_rate = (avg_revenue - older_avg) / older_avg
    else:
        avg_revenue = sum(m["revenue"] for m in monthly_revenue) / len(monthly_revenue) if monthly_revenue else 0
        growth_rate = 0

    # Forecast future months
    forecast = []
    for i in range(1, months + 1):
        future_month = today + timedelta(days=30 * i)
        projected = avg_revenue * ((1 + growth_rate) ** i)
        forecast.append({
            "month": future_month.strftime("%b %Y"),
            "projected": round(projected, 2),
            "low": round(projected * 0.7, 2),
            "high": round(projected * 1.3, 2),
        })

    # Package performance
    from apps.packages.models import Package
    package_stats = Invoice.objects.filter(
        studio=studio,
        status="paid",
        booking__package__isnull=False,
    ).values(
        "booking__package__name"
    ).annotate(
        total_revenue=Sum("total"),
        count=Count("id"),
    ).order_by("-total_revenue")[:5]

    return {
        "monthly_revenue": monthly_revenue,
        "forecast": forecast,
        "avg_monthly": round(avg_revenue, 2),
        "growth_rate": round(growth_rate * 100, 1),
        "package_stats": list(package_stats),
    }
