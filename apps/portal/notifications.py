import json
import logging

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


def notify_client_portal(client_id, event_type, data):
    """Send a real-time notification to a client's portal WebSocket.

    Args:
        client_id: UUID of the Client record.
        event_type: One of 'notification', 'booking_update', 'payment_confirmed', 'gallery_ready'.
        data: Dict payload to send.
    """
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"portal_{client_id}",
            {
                "type": event_type,
                "data": data,
            },
        )
    except Exception:
        logger.exception("Failed to send portal notification to client %s", client_id)


def notify_booking_update(booking):
    """Notify client portal about a booking status change."""
    notify_client_portal(
        client_id=str(booking.client_id),
        event_type="booking_update",
        data={
            "title": "Booking Updated",
            "message": f"Your booking {booking.reference} is now {booking.get_status_display()}.",
            "booking_id": str(booking.pk),
            "status": booking.status,
        },
    )


def notify_payment_confirmed(payment):
    """Notify client portal about a confirmed payment."""
    notify_client_portal(
        client_id=str(payment.client_id),
        event_type="payment_confirmed",
        data={
            "title": "Payment Received",
            "message": f"Payment of N{payment.amount:,.2f} confirmed. Ref: {payment.reference}",
            "payment_id": str(payment.pk),
            "amount": str(payment.amount),
        },
    )


def notify_gallery_ready(gallery):
    """Notify client portal that a gallery is ready for viewing."""
    notify_client_portal(
        client_id=str(gallery.project.client_id),
        event_type="gallery_ready",
        data={
            "title": "Gallery Ready",
            "message": f'Your gallery "{gallery.title}" is ready for viewing.',
            "gallery_id": str(gallery.pk),
        },
    )
