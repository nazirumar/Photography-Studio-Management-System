import io
from datetime import date, timedelta
from decimal import Decimal

from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Sum, Count, Q, F
from django.utils import timezone

from apps.accounts.services import get_user_studio
from apps.accounts.decorators import login_required
from apps.finance.models import Invoice, Payment
from apps.bookings.models import Booking
from apps.clients.models import Client
from apps.expenses.models import Expense


@login_required
def advanced_reports(request):
    """Advanced reporting dashboard with custom date ranges."""
    studio = get_user_studio(request.user)
    today = date.today()

    # Date range from query params
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date:
        start_date = date.fromisoformat(start_date)
    else:
        start_date = today.replace(day=1)

    if end_date:
        end_date = date.fromisoformat(end_date)
    else:
        end_date = today

    # Revenue
    revenue = Payment.objects.filter(
        studio=studio,
        payment_date__gte=start_date,
        payment_date__lte=end_date,
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    # Expenses
    expenses = Expense.objects.filter(
        studio=studio,
        date__gte=start_date,
        date__lte=end_date,
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    # Bookings
    bookings_count = Booking.objects.filter(
        studio=studio,
        date__gte=start_date,
        date__lte=end_date,
    ).count()

    # New clients
    new_clients = Client.objects.filter(
        studio=studio,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
    ).count()

    # Revenue by month
    revenue_by_month = []
    current = start_date
    while current <= end_date:
        month_start = current.replace(day=1)
        if current.month == 12:
            month_end = current.replace(year=current.year + 1, month=1, day=1)
        else:
            month_end = current.replace(month=current.month + 1, day=1)

        rev = Payment.objects.filter(
            studio=studio,
            payment_date__gte=month_start,
            payment_date__lt=month_end,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        exp = Expense.objects.filter(
            studio=studio,
            date__gte=month_start,
            date__lt=month_end,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        revenue_by_month.append({
            "month": current.strftime("%b %Y"),
            "revenue": float(rev),
            "expenses": float(exp),
            "profit": float(rev - exp),
        })

        current = month_end

    # Top clients
    top_clients = Client.objects.filter(
        studio=studio,
        bookings__date__gte=start_date,
        bookings__date__lte=end_date,
    ).annotate(
        total_spent=Sum("bookings__payments__amount"),
        booking_count=Count("bookings"),
    ).order_by("-total_spent")[:10]

    # Revenue by event type
    revenue_by_event = Booking.objects.filter(
        studio=studio,
        date__gte=start_date,
        date__lte=end_date,
    ).values("event_type").annotate(
        total=Sum("total_amount"),
        count=Count("id"),
    ).order_by("-total")[:10]

    context = {
        "start_date": start_date,
        "end_date": end_date,
        "revenue": revenue,
        "expenses": expenses,
        "profit": revenue - expenses,
        "bookings_count": bookings_count,
        "new_clients": new_clients,
        "revenue_by_month": revenue_by_month,
        "top_clients": top_clients,
        "revenue_by_event": revenue_by_event,
    }

    return render(request, "reports/advanced.html", context)


@login_required
def export_report_csv(request, report_type):
    """Export report data as CSV."""
    studio = get_user_studio(request.user)
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date:
        start_date = date.fromisoformat(start_date)
    else:
        start_date = date.today().replace(day=1)

    if end_date:
        end_date = date.fromisoformat(end_date)
    else:
        end_date = date.today()

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{report_type}_report.csv"'

    import csv
    writer = csv.writer(response)

    if report_type == "revenue":
        writer.writerow(["Date", "Reference", "Client", "Amount", "Method"])
        payments = Payment.objects.filter(
            studio=studio,
            payment_date__gte=start_date,
            payment_date__lte=end_date,
        ).select_related("client")
        for p in payments:
            writer.writerow([p.payment_date, p.reference, p.client.display_name, p.amount, p.get_method_display()])

    elif report_type == "bookings":
        writer.writerow(["Date", "Reference", "Client", "Event Type", "Status", "Amount"])
        bookings = Booking.objects.filter(
            studio=studio,
            date__gte=start_date,
            date__lte=end_date,
        ).select_related("client")
        for b in bookings:
            writer.writerow([b.date, b.reference, b.client.display_name, b.event_type, b.get_status_display(), b.total_amount])

    elif report_type == "expenses":
        writer.writerow(["Date", "Reference", "Category", "Description", "Amount", "Vendor"])
        expenses = Expense.objects.filter(
            studio=studio,
            date__gte=start_date,
            date__lte=end_date,
        ).select_related("category")
        for e in expenses:
            writer.writerow([e.date, e.reference, e.category.name if e.category else "", e.description, e.amount, e.vendor])

    return response
