from datetime import date, timedelta
from django.db.models import Q

from apps.bookings.models import Booking
from apps.equipment.models import Equipment


def check_photographer_conflicts(studio, photographer, booking_date, exclude_booking=None):
    """Check if photographer has conflicts on the given date."""
    conflicts = Booking.objects.filter(
        studio=studio,
        photographer=photographer,
        date=booking_date,
        status__in=["confirmed", "in_progress", "awaiting_deposit"],
    )
    if exclude_booking:
        conflicts = conflicts.exclude(pk=exclude_booking.pk)
    return list(conflicts)


def check_equipment_conflicts(studio, equipment, booking_date, start_time=None, end_time=None, exclude_booking=None):
    """Check if equipment is already reserved for the given date/time."""
    conflicts = Booking.objects.filter(
        studio=studio,
        equipment=equipment,
        date=booking_date,
        status__in=["confirmed", "in_progress", "awaiting_deposit"],
    )
    if exclude_booking:
        conflicts = conflicts.exclude(pk=exclude_booking.pk)
    if start_time and end_time:
        conflicts = conflicts.filter(
            Q(start_time__lt=end_time, end_time__gt=start_time)
        )
    return list(conflicts)


def check_location_conflicts(studio, location, booking_date, start_time=None, end_time=None, exclude_booking=None):
    """Check if location is already booked."""
    conflicts = Booking.objects.filter(
        studio=studio,
        location=location,
        date=booking_date,
        status__in=["confirmed", "in_progress", "awaiting_deposit"],
    )
    if exclude_booking:
        conflicts = conflicts.exclude(pk=exclude_booking.pk)
    if start_time and end_time:
        conflicts = conflicts.filter(
            Q(start_time__lt=end_time, end_time__gt=start_time)
        )
    return list(conflicts)


def check_all_conflicts(studio, booking_date, photographer=None, equipment_ids=None, location=None, start_time=None, end_time=None, exclude_booking=None):
    """Check all conflicts for a booking."""
    results = {
        "photographer_conflicts": [],
        "equipment_conflicts": [],
        "location_conflicts": [],
    }

    if photographer:
        results["photographer_conflicts"] = check_photographer_conflicts(
            studio, photographer, booking_date, exclude_booking
        )

    if equipment_ids:
        for eq_id in equipment_ids:
            try:
                equipment = Equipment.objects.get(pk=eq_id, studio=studio)
                conflicts = check_equipment_conflicts(
                    studio, equipment, booking_date, start_time, end_time, exclude_booking
                )
                if conflicts:
                    results["equipment_conflicts"].append({
                        "equipment": equipment,
                        "conflicts": conflicts,
                    })
            except Equipment.DoesNotExist:
                pass

    if location:
        results["location_conflicts"] = check_location_conflicts(
            studio, location, booking_date, start_time, end_time, exclude_booking
        )

    return results


def get_available_photographers(studio, booking_date, start_time=None, end_time=None):
    """Get photographers available on the given date."""
    from apps.accounts.models import StaffProfile

    booked_photographers = Booking.objects.filter(
        studio=studio,
        date=booking_date,
        status__in=["confirmed", "in_progress", "awaiting_deposit"],
    ).values_list("photographer_id", flat=True)

    staff_profiles = StaffProfile.objects.filter(
        studio=studio,
        role__in=["photographer", "admin"],
        user__is_active=True,
    ).exclude(user_id__in=booked_photographers)

    return [sp.user for sp in staff_profiles]


def get_available_equipment(studio, booking_date, start_time=None, end_time=None):
    """Get equipment available on the given date."""
    booked_equipment = Booking.objects.filter(
        studio=studio,
        date=booking_date,
        status__in=["confirmed", "in_progress", "awaiting_deposit"],
    ).values_list("equipment_id", flat=True)

    return Equipment.objects.filter(
        studio=studio,
        status="available",
    ).exclude(pk__in=booked_equipment)


def get_booking_conflicts_summary(studio, days=7):
    """Get summary of booking conflicts for next N days."""
    today = date.today()
    end_date = today + timedelta(days=days)

    bookings = Booking.objects.filter(
        studio=studio,
        date__gte=today,
        date__lte=end_date,
        status__in=["confirmed", "in_progress", "awaiting_deposit"],
    ).select_related("photographer", "client")

    conflicts = []
    for booking in bookings:
        photographer_conflicts = check_photographer_conflicts(
            studio, booking.photographer, booking.date, exclude_booking=booking
        )
        if photographer_conflicts:
            conflicts.append({
                "booking": booking,
                "type": "photographer",
                "conflicts": photographer_conflicts,
            })

    return conflicts
