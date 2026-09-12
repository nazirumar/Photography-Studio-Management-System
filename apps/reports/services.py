from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone

from apps.bookings.models import Booking
from apps.clients.models import Client
from apps.expenses.models import Expense
from apps.finance.models import Invoice, Payment
from apps.gallery.models import Photo
from apps.leads.models import Lead
from apps.packages.models import Package
from apps.projects.models import Project


def get_revenue_report(studio, start_date=None, end_date=None):
    """Get revenue report for a date range."""
    if not start_date:
        start_date = timezone.now().date() - timedelta(days=30)
    if not end_date:
        end_date = timezone.now().date()

    payments = Payment.objects.filter(
        invoice__booking__studio=studio,
        payment_date__range=[start_date, end_date],
    ).select_related("invoice", "invoice__booking", "invoice__booking__client")

    total_revenue = payments.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    payment_count = payments.count()

    by_method = list(
        payments.values("method").annotate(
            total=Sum("amount"), count=Count("id")
        ).order_by("-total")
    )

    return {
        "total_revenue": total_revenue,
        "payment_count": payment_count,
        "by_method": by_method,
        "start_date": start_date,
        "end_date": end_date,
    }


def get_expense_report(studio, start_date=None, end_date=None):
    """Get expense report for a date range."""
    if not start_date:
        start_date = timezone.now().date() - timedelta(days=30)
    if not end_date:
        end_date = timezone.now().date()

    expenses = Expense.objects.filter(
        studio=studio, date__range=[start_date, end_date]
    )

    total_expenses = expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0")

    by_category = list(
        expenses.values("category").annotate(
            total=Sum("amount"), count=Count("id")
        ).order_by("-total")
    )

    return {
        "total_expenses": total_expenses,
        "by_category": by_category,
        "start_date": start_date,
        "end_date": end_date,
    }


def get_booking_report(studio, start_date=None, end_date=None):
    """Get booking statistics for a date range."""
    if not start_date:
        start_date = timezone.now().date() - timedelta(days=30)
    if not end_date:
        end_date = timezone.now().date()

    bookings = Booking.objects.filter(
        studio=studio, date__range=[start_date, end_date]
    ).select_related("client", "package")
    total = bookings.count()
    by_status = list(
        bookings.values("status").annotate(count=Count("id")).order_by("status")
    )
    total_revenue = bookings.aggregate(total=Sum("total_amount"))["total"] or Decimal("0")

    return {
        "total_bookings": total,
        "by_status": by_status,
        "total_revenue": total_revenue,
        "start_date": start_date,
        "end_date": end_date,
    }


def get_client_report(studio):
    """Get client statistics."""
    total_clients = Client.objects.filter(studio=studio).count()
    active_clients = Client.objects.filter(
        studio=studio, bookings__status__in=["confirmed", "awaiting_deposit", "completed"]
    ).distinct().count()
    total_lifetime_value = Client.objects.filter(studio=studio).aggregate(
        total=Sum("bookings__payments__amount")
    )["total"] or Decimal("0")

    top_clients = list(
        Client.objects.filter(studio=studio)
        .select_related("assigned_to", "studio")
        .annotate(total_spent=Sum("bookings__payments__amount"))
        .order_by("-total_spent")[:10]
    )

    return {
        "total_clients": total_clients,
        "active_clients": active_clients,
        "total_lifetime_value": total_lifetime_value,
        "top_clients": top_clients,
    }


def get_lead_conversion_report(studio):
    """Get lead conversion statistics."""
    total_leads = Lead.objects.filter(studio=studio).count()
    converted = Lead.objects.filter(studio=studio, status="won").count()
    conversion_rate = (converted / total_leads * 100) if total_leads > 0 else 0

    by_source = list(
        Lead.objects.filter(studio=studio)
        .values("source")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    return {
        "total_leads": total_leads,
        "converted": converted,
        "conversion_rate": round(conversion_rate, 1),
        "by_source": by_source,
    }


def get_package_report(studio):
    """Get package popularity and revenue."""
    packages = Package.objects.filter(studio=studio, is_active=True)
    popular = list(
        packages.annotate(booking_count=Count("bookings"))
        .order_by("-booking_count")[:10]
    )
    return {
        "popular_packages": popular,
    }


def get_gallery_report(studio):
    """Get gallery and photo statistics."""
    total_photos = Photo.objects.filter(gallery__project__studio=studio).count()
    selected_photos = Photo.objects.filter(
        gallery__project__studio=studio, is_selected=True
    ).count()
    total_galleries = Project.objects.filter(studio=studio).exclude(galleries=None).count()

    return {
        "total_photos": total_photos,
        "selected_photos": selected_photos,
        "total_galleries": total_galleries,
    }


def get_financial_summary(studio):
    """Get overall financial summary."""
    today = timezone.now().date()
    month_start = today.replace(day=1)

    monthly_revenue = Payment.objects.filter(
        invoice__booking__studio=studio,
        payment_date__gte=month_start,
    ).select_related("invoice", "invoice__booking").aggregate(total=Sum("amount"))["total"] or Decimal("0")

    monthly_expenses = Expense.objects.filter(
        studio=studio, date__gte=month_start,
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    outstanding = Invoice.objects.filter(
        booking__studio=studio, status="issued"
    ).select_related("booking", "client").aggregate(total=Sum("balance"))["total"] or Decimal("0")

    return {
        "monthly_revenue": monthly_revenue,
        "monthly_expenses": monthly_expenses,
        "net_profit": monthly_revenue - monthly_expenses,
        "outstanding_invoices": outstanding,
    }
