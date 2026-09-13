from datetime import date as dt_date
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from apps.accounts.services import get_user_studio
from apps.reports.services import (
    get_booking_report,
    get_client_report,
    get_expense_report,
    get_financial_summary,
    get_gallery_report,
    get_lead_conversion_report,
    get_package_report,
    get_revenue_report,
)


@login_required
def reports_dashboard(request):
    studio = get_user_studio(request.user)
    financial = get_financial_summary(studio)
    return render(request, "reports/dashboard.html", {"financial": financial})


def _parse_date_range(request):
    start_date = request.GET.get("start_date") or (timezone.now().date() - timedelta(days=30))
    end_date = request.GET.get("end_date") or timezone.now().date()
    if not hasattr(start_date, "strftime"):
        start_date = dt_date.fromisoformat(str(start_date))
        end_date = dt_date.fromisoformat(str(end_date))
    return start_date, end_date


@login_required
def revenue_report(request):
    studio = get_user_studio(request.user)
    start_date, end_date = _parse_date_range(request)
    report = get_revenue_report(studio, start_date, end_date)
    return render(request, "reports/revenue.html", report)


@login_required
def expense_report(request):
    studio = get_user_studio(request.user)
    start_date, end_date = _parse_date_range(request)
    report = get_expense_report(studio, start_date, end_date)
    return render(request, "reports/expenses.html", report)


@login_required
def booking_report(request):
    studio = get_user_studio(request.user)
    start_date, end_date = _parse_date_range(request)
    report = get_booking_report(studio, start_date, end_date)
    return render(request, "reports/bookings.html", report)


@login_required
def client_report(request):
    studio = get_user_studio(request.user)
    report = get_client_report(studio)
    return render(request, "reports/clients.html", report)


@login_required
def lead_report(request):
    studio = get_user_studio(request.user)
    report = get_lead_conversion_report(studio)
    return render(request, "reports/leads.html", report)


@login_required
def package_report(request):
    studio = get_user_studio(request.user)
    report = get_package_report(studio)
    return render(request, "reports/packages.html", report)


@login_required
def gallery_report(request):
    studio = get_user_studio(request.user)
    report = get_gallery_report(studio)
    return render(request, "reports/gallery.html", report)


@login_required
def revenue_forecast(request):
    """Revenue forecasting dashboard."""
    studio = get_user_studio(request.user)
    from apps.reports.forecast_service import get_revenue_forecast
    forecast_data = get_revenue_forecast(studio)
    return render(request, "reports/forecast.html", {"forecast": forecast_data})
