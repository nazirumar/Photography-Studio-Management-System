import json
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio
from apps.staff.models import StaffSchedule, StaffBooking


@login_required
def staff_schedule_view(request):
    """View and manage staff weekly schedules."""
    studio = get_user_studio(request.user)
    from apps.accounts.models import User
    staff_members = User.objects.filter(staff_profile__studio=studio).select_related("staff_profile")

    staff_id = request.GET.get("staff")
    selected_staff = None
    schedules = StaffSchedule.objects.filter(studio=studio)

    if staff_id:
        selected_staff = staff_members.filter(pk=staff_id).first()
        if selected_staff:
            schedules = schedules.filter(staff=selected_staff)

    # Group by day
    days = {}
    for day_num, day_name in StaffSchedule.DayOfWeek.choices:
        days[day_num] = {
            "name": day_name,
            "schedules": schedules.filter(day_of_week=day_num).order_by("start_time"),
        }

    if request.method == "POST":
        staff_pk = request.POST.get("staff_pk")
        day = request.POST.get("day_of_week")
        start = request.POST.get("start_time")
        end = request.POST.get("end_time")
        available = request.POST.get("is_available") == "on"

        if staff_pk and day and start and end:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            staff = User.objects.get(pk=staff_pk)
            schedule, created = StaffSchedule.objects.update_or_create(
                studio=studio, staff=staff, day_of_week=int(day), start_time=start,
                defaults={"end_time": end, "is_available": available},
            )
            messages.success(request, f"Schedule {'added' if created else 'updated'}.")
        return redirect("staff:schedule")

    return render(request, "staff/schedule.html", {
        "staff_members": staff_members,
        "selected_staff": selected_staff,
        "days": days,
        "day_choices": StaffSchedule.DayOfWeek.choices,
    })


@login_required
def staff_available_api(request):
    """API: Get available staff for a given date/time."""
    studio = get_user_studio(request.user)
    date_str = request.GET.get("date")
    time_str = request.GET.get("time")

    if not date_str:
        return JsonResponse({"staff": []})

    try:
        check_date = date.fromisoformat(date_str)
        day_of_week = check_date.weekday()
    except ValueError:
        return JsonResponse({"error": "Invalid date"}, status=400)

    available_schedules = StaffSchedule.objects.filter(
        studio=studio, day_of_week=day_of_week, is_available=True
    ).select_related("staff")

    if time_str:
        available_schedules = available_schedules.filter(start_time__lte=time_str, end_time__gte=time_str)

    staff_list = []
    for s in available_schedules:
        staff_list.append({
            "id": str(s.staff.pk),
            "name": f"{s.staff.first_name} {s.staff.last_name}",
            "email": s.staff.email,
            "start_time": s.start_time.strftime("%H:%M"),
            "end_time": s.end_time.strftime("%H:%M"),
        })

    return JsonResponse({"staff": staff_list})


@login_required
def staff_booking_assign(request, booking_pk):
    """Assign staff to a booking."""
    studio = get_user_studio(request.user)
    from apps.bookings.models import Booking
    booking = get_object_or_404(Booking, pk=booking_pk, studio=studio)

    if request.method == "POST":
        staff_id = request.POST.get("staff_id")
        role = request.POST.get("role", "")
        if staff_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            staff = User.objects.get(pk=staff_id)
            StaffBooking.objects.get_or_create(
                studio=studio, booking=booking, staff=staff,
                defaults={"role": role},
            )
            messages.success(request, f"{staff.get_full_name()} assigned to booking.")
        return redirect("bookings:detail", pk=booking.pk)

    from django.contrib.auth import get_user_model
    User = get_user_model()
    staff_members = User.objects.filter(staff_profile__studio=studio)
    assigned = StaffBooking.objects.filter(booking=booking).select_related("staff", "staff__staff_profile")

    return render(request, "staff/assign.html", {
        "booking": booking,
        "staff_members": staff_members,
        "assigned": assigned,
    })
