from datetime import date

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from apps.accounts.services import get_user_studio

from .conflict_service import (
    check_all_conflicts,
    get_available_photographers,
    get_available_equipment,
    get_booking_conflicts_summary,
)


@login_required
def check_conflicts_api(request):
    """API endpoint to check conflicts for a date."""
    studio = get_user_studio(request.user)
    booking_date = request.GET.get("date")
    photographer_id = request.GET.get("photographer")
    equipment_ids = request.GET.getlist("equipment")
    location = request.GET.get("location")
    start_time = request.GET.get("start_time")
    end_time = request.GET.get("end_time")
    exclude_id = request.GET.get("exclude")

    if not booking_date:
        return JsonResponse({"error": "Date is required"}, status=400)

    from apps.bookings.models import Booking
    exclude_booking = None
    if exclude_id:
        try:
            exclude_booking = Booking.objects.get(pk=exclude_id, studio=studio)
        except Booking.DoesNotExist:
            pass

    from apps.accounts.models import User
    photographer = None
    if photographer_id:
        try:
            photographer = User.objects.get(pk=photographer_id)
        except User.DoesNotExist:
            pass

    conflicts = check_all_conflicts(
        studio=studio,
        booking_date=booking_date,
        photographer=photographer,
        equipment_ids=equipment_ids if equipment_ids else None,
        location=location,
        start_time=start_time,
        end_time=end_time,
        exclude_booking=exclude_booking,
    )

    result = {
        "has_conflicts": any([
            conflicts["photographer_conflicts"],
            conflicts["equipment_conflicts"],
            conflicts["location_conflicts"],
        ]),
        "photographer_available": len(conflicts["photographer_conflicts"]) == 0,
        "equipment_available": len(conflicts["equipment_conflicts"]) == 0,
        "location_available": len(conflicts["location_conflicts"]) == 0,
    }

    if conflicts["photographer_conflicts"]:
        result["photographer_conflicts"] = [
            {"id": b.pk, "title": b.title or b.reference, "client": str(b.client)}
            for b in conflicts["photographer_conflicts"]
        ]

    return JsonResponse(result)


@login_required
def available_photographers_api(request):
    """API endpoint to get available photographers."""
    studio = get_user_studio(request.user)
    booking_date = request.GET.get("date")

    if not booking_date:
        return JsonResponse({"error": "Date is required"}, status=400)

    photographers = get_available_photographers(studio, booking_date)
    return JsonResponse({
        "photographers": [{"id": p.pk, "name": str(p)} for p in photographers]
    })


@login_required
def available_equipment_api(request):
    """API endpoint to get available equipment."""
    studio = get_user_studio(request.user)
    booking_date = request.GET.get("date")

    if not booking_date:
        return JsonResponse({"error": "Date is required"}, status=400)

    equipment = get_available_equipment(studio, booking_date)
    return JsonResponse({
        "equipment": [{"id": e.pk, "name": str(e)} for e in equipment]
    })


@login_required
def conflicts_dashboard(request):
    """View showing booking conflicts."""
    studio = get_user_studio(request.user)
    conflicts = get_booking_conflicts_summary(studio, days=14)
    return render(request, "bookings/conflicts.html", {"conflicts": conflicts})
