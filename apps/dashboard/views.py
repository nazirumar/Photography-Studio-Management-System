import json
from calendar import month_abbr
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone

from apps.accounts.services import get_user_studio
from apps.bookings.models import Booking
from apps.clients.models import Client
from apps.equipment.models import Equipment
from apps.expenses.models import Expense
from apps.finance.models import Invoice, Payment
from apps.leads.models import Lead
from apps.notifications.services import get_unread_count


@login_required
def dashboard_view(request):
    studio = get_user_studio(request.user)
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Financial summary
    monthly_revenue = Payment.objects.filter(
        invoice__booking__studio=studio,
        payment_date__gte=month_start,
    ).select_related("invoice", "invoice__booking").aggregate(total=Sum("amount"))["total"] or Decimal("0")
    monthly_expenses = Expense.objects.filter(
        studio=studio, date__gte=month_start,
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    # Bookings
    upcoming_bookings = Booking.objects.filter(
        studio=studio, date__gte=today, status__in=["confirmed", "awaiting_deposit"]
    ).select_related("client", "package", "photographer").order_by("date")[:5]
    total_bookings = Booking.objects.filter(studio=studio, date__month=today.month).count()

    # Clients & Leads
    total_clients = Client.objects.filter(studio=studio).count()
    new_leads = Lead.objects.filter(studio=studio, status="new").count()

    # Outstanding
    outstanding = Invoice.objects.filter(
        booking__studio=studio, status__in=["issued", "partial"]
    ).select_related("booking", "client").count()

    # Notifications
    unread = get_unread_count(request.user)

    # Equipment maintenance
    overdue_maintenance = Equipment.objects.filter(
        studio=studio,
        next_maintenance__lt=today,
        status__in=["available", "in_use", "maintenance"],
    ).count()

    # Chart data - last 6 months
    revenue_data = []
    bookings_data = []
    for i in range(5, -1, -1):
        d = today.replace(day=1)
        for _ in range(i):
            if d.month == 1:
                d = d.replace(year=d.year - 1, month=12)
            else:
                d = d.replace(month=d.month - 1)
        month_start_c = d.replace(day=1)
        if d.month == 12:
            month_end_c = d.replace(year=d.year + 1, month=1, day=1)
        else:
            month_end_c = d.replace(month=d.month + 1, day=1)

        rev = Payment.objects.filter(
            invoice__booking__studio=studio,
            payment_date__gte=month_start_c,
            payment_date__lt=month_end_c,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        bkg_count = Booking.objects.filter(
            studio=studio, date__gte=month_start_c, date__lt=month_end_c,
        ).count()
        revenue_data.append({"month": month_abbr[d.month], "amount": float(rev)})
        bookings_data.append({"month": month_abbr[d.month], "count": bkg_count})

    return render(request, "dashboard/index.html", {
        "monthly_revenue": monthly_revenue,
        "monthly_expenses": monthly_expenses,
        "upcoming_bookings": upcoming_bookings,
        "total_bookings": total_bookings,
        "total_clients": total_clients,
        "new_leads": new_leads,
        "outstanding_invoices": outstanding,
        "overdue_maintenance": overdue_maintenance,
        "unread_notifications": unread,
        "revenue_chart_data": json.dumps(revenue_data),
        "bookings_chart_data": json.dumps(bookings_data),
    })
