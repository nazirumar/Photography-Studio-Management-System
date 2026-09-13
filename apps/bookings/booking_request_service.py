from datetime import datetime
from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditLog


def create_booking_request(studio, data):
    """Create a new booking request from public form submission."""
    from apps.bookings.models import BookingRequest
    with transaction.atomic():
        request_obj = BookingRequest.objects.create(studio=studio, **data)
        AuditLog.objects.create(
            studio=studio,
            action="booking_request_created",
            entity_type="BookingRequest",
            entity_id=str(request_obj.pk),
            after_values={
                "name": f"{request_obj.first_name} {request_obj.last_name}",
                "event_type": request_obj.event_type,
                "preferred_date": str(request_obj.preferred_date),
            },
        )
        return request_obj


def review_booking_request(booking_request, user, approved=True):
    """Staff reviews a booking request."""
    from apps.bookings.models import BookingRequest
    with transaction.atomic():
        old_status = booking_request.status
        new_status = BookingRequest.Status.APPROVED if approved else BookingRequest.Status.DECLINED
        booking_request.status = new_status
        booking_request.reviewed_by = user
        booking_request.reviewed_at = timezone.now()
        booking_request.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])
        AuditLog.objects.create(
            studio=booking_request.studio,
            user=user,
            action="booking_request_reviewed",
            entity_type="BookingRequest",
            entity_id=str(booking_request.pk),
            before_values={"status": old_status},
            after_values={"status": new_status},
        )
        return booking_request


def convert_request_to_booking(booking_request, user):
    """Convert an approved booking request to a booking."""
    from apps.bookings.models import BookingRequest
    from apps.bookings.services import create_booking
    from apps.clients.services import create_client
    from apps.studios.services import get_studio_for_user

    studio = booking_request.studio
    with transaction.atomic():
        client_data = {
            "first_name": booking_request.first_name,
            "last_name": booking_request.last_name,
            "email": booking_request.email,
            "phone": booking_request.phone,
            "whatsapp": booking_request.whatsapp,
        }
        client = create_client(studio, client_data, user)

        booking_data = {
            "client": client,
            "package": booking_request.package,
            "date": booking_request.preferred_date,
            "title": f"{booking_request.event_type} - {booking_request.first_name} {booking_request.last_name}",
            "event_type": booking_request.event_type,
            "location_type": booking_request.location_preference if booking_request.location_preference != "no_preference" else "studio",
            "total_amount": booking_request.budget or 0,
        }
        booking = create_booking(studio, booking_data, user)

        booking_request.status = BookingRequest.Status.CONVERTED
        booking_request.converted_booking = booking
        booking_request.save(update_fields=["status", "converted_booking", "updated_at"])

        return booking
