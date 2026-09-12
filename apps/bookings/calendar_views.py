import calendar as cal_module
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.accounts.services import get_user_studio
from apps.bookings.models import Booking


STATUS_COLORS = {
    "enquiry": {"bg": "bg-gray-100", "text": "text-gray-700", "dot": "bg-gray-400"},
    "tentative": {"bg": "bg-amber-50", "text": "text-amber-700", "dot": "bg-amber-400"},
    "awaiting_deposit": {"bg": "bg-yellow-50", "text": "text-yellow-700", "dot": "bg-yellow-400"},
    "confirmed": {"bg": "bg-green-50", "text": "text-green-700", "dot": "bg-green-500"},
    "in_progress": {"bg": "bg-blue-50", "text": "text-blue-700", "dot": "bg-blue-500"},
    "completed": {"bg": "bg-emerald-50", "text": "text-emerald-700", "dot": "bg-emerald-500"},
    "cancelled": {"bg": "bg-red-50", "text": "text-red-600", "dot": "bg-red-400"},
    "no_show": {"bg": "bg-red-50", "text": "text-red-600", "dot": "bg-red-400"},
}


@login_required
def booking_calendar(request):
    studio = get_user_studio(request.user)

    year = request.GET.get("year")
    month = request.GET.get("month")

    today = date.today()
    try:
        year = int(year) if year else today.year
        month = int(month) if month else today.month
    except (ValueError, TypeError):
        year, month = today.year, today.month

    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    first_day = date(year, month, 1)
    last_day = date(year, month, cal_module.monthrange(year, month)[1])

    bookings = Booking.objects.filter(
        studio=studio,
        date__gte=first_day,
        date__lte=last_day,
    ).select_related("client", "package").order_by("date", "start_time")

    bookings_by_date = {}
    for booking in bookings:
        day = booking.date.day
        if day not in bookings_by_date:
            bookings_by_date[day] = []
        bookings_by_date[day].append(booking)

    month_calendar = cal_module.monthcalendar(year, month)

    prev_month = (year, month - 1) if month > 1 else (year - 1, 12)
    next_month = (year, month + 1) if month < 12 else (year + 1, 1)

    return render(request, "bookings/calendar.html", {
        "year": year,
        "month": month,
        "month_name": cal_module.month_name[month],
        "today": today,
        "calendar": month_calendar,
        "bookings_by_date": bookings_by_date,
        "status_colors": STATUS_COLORS,
        "prev_month": prev_month,
        "next_month": next_month,
    })
