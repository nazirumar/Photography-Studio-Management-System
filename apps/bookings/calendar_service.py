from datetime import datetime, timedelta
from icalendar import Calendar, Event


def generate_booking_ical(booking):
    """Generate an iCal file for a single booking."""
    cal = Calendar()
    cal.add("prodid", "-//StudioFlow//Booking//EN")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", f"StudioFlow - {booking.reference}")

    event = Event()
    event.add("summary", f"{booking.title or booking.event_type} - {booking.client}")
    event.add("dtstart", datetime.combine(booking.date, booking.start_time or datetime.min.time()))
    if booking.end_time:
        event.add("dtend", datetime.combine(booking.date, booking.end_time))
    else:
        event.add("dtend", datetime.combine(booking.date, datetime.min.time()) + timedelta(hours=2))
    event.add("location", booking.location or "Studio")
    event.add("description", (
        f"Booking: {booking.reference}\n"
        f"Client: {booking.client}\n"
        f"Package: {booking.package.name if booking.package else 'N/A'}\n"
        f"Status: {booking.get_status_display()}\n"
        f"Amount: ₦{booking.total_amount:,.2f}"
    ))
    event.add("status", "CONFIRMED" if booking.status == "confirmed" else "TENTATIVE")

    if booking.photographer:
        event.add("organizer", f"mailto:{booking.photographer.email}")

    cal.add_component(event)
    return cal.to_ical()


def generate_studio_calendar(bookings):
    """Generate an iCal file for multiple bookings."""
    cal = Calendar()
    cal.add("prodid", "-//StudioFlow//StudioCalendar//EN")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", "StudioFlow Bookings")

    for booking in bookings:
        event = Event()
        event.add("summary", f"{booking.title or booking.event_type} - {booking.client}")
        event.add("dtstart", datetime.combine(booking.date, booking.start_time or datetime.min.time()))
        if booking.end_time:
            event.add("dtend", datetime.combine(booking.date, booking.end_time))
        else:
            event.add("dtend", datetime.combine(booking.date, datetime.min.time()) + timedelta(hours=2))
        event.add("location", booking.location or "Studio")
        event.add("uid", f"{booking.pk}@studioflow")
        event.add("status", "CONFIRMED" if booking.status == "confirmed" else "TENTATIVE")
        cal.add_component(event)

    return cal.to_ical()
