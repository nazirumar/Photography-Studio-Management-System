from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@shared_task
def send_booking_confirmation(booking_id):
    """Send booking confirmation email to client."""
    from apps.bookings.models import Booking
    booking = Booking.objects.select_related("client", "package").get(pk=booking_id)
    subject = f"Booking Confirmed - {booking.reference}"
    html_message = render_to_string("emails/booking_confirmation.html", {"booking": booking})
    plain_message = strip_tags(html_message)
    send_mail(
        subject, plain_message, None,
        [booking.client.email], html_message=html_message,
    )


@shared_task
def send_payment_receipt(payment_id):
    """Send payment receipt email."""
    from apps.finance.models import Payment
    payment = Payment.objects.select_related("client", "invoice").get(pk=payment_id)
    subject = f"Payment Receipt - {payment.reference}"
    html_message = render_to_string("emails/payment_receipt.html", {"payment": payment})
    plain_message = strip_tags(html_message)
    send_mail(
        subject, plain_message, None,
        [payment.client.email], html_message=html_message,
    )


@shared_task
def send_selection_ready(gallery_id):
    """Send photo selection ready notification."""
    from apps.gallery.models import Gallery
    gallery = Gallery.objects.select_related("project__client").get(pk=gallery_id)
    subject = "Your photos are ready for selection!"
    html_message = render_to_string("emails/selection_ready.html", {"gallery": gallery})
    plain_message = strip_tags(html_message)
    send_mail(
        subject, plain_message, None,
        [gallery.project.client.email], html_message=html_message,
    )


@shared_task
def send_delivery_notification(project_id):
    """Send delivery notification."""
    from apps.projects.models import Project
    project = Project.objects.select_related("client").get(pk=project_id)
    subject = f"Project Ready for Delivery - {project.reference}"
    html_message = render_to_string("emails/delivery_notification.html", {"project": project})
    plain_message = strip_tags(html_message)
    send_mail(
        subject, plain_message, None,
        [project.client.email], html_message=html_message,
    )


@shared_task
def send_invoice_email(invoice_id):
    """Send invoice via email."""
    from apps.finance.models import Invoice
    invoice = Invoice.objects.select_related("client").get(pk=invoice_id)
    subject = f"Invoice {invoice.invoice_number}"
    html_message = render_to_string("emails/invoice_email.html", {"invoice": invoice})
    plain_message = strip_tags(html_message)
    send_mail(
        subject, plain_message, None,
        [invoice.client.email], html_message=html_message,
    )


@shared_task
def send_low_stock_alert(item_id):
    """Send low stock alert to studio admin."""
    from apps.accounts.models import StaffProfile
    from apps.inventory.models import InventoryItem
    item = InventoryItem.objects.get(pk=item_id)
    admins = StaffProfile.objects.filter(
        studio=item.studio, role__in=["owner", "manager"]
    ).select_related("user")
    for admin in admins:
        send_mail(
            f"Low Stock Alert: {item.name}",
            f"{item.name} is running low. Current: {item.quantity}, Reorder: {item.reorder_level}",
            None, [admin.user.email],
        )


@shared_task
def send_maintenance_reminder(equipment_id):
    """Send equipment maintenance reminder."""
    from apps.accounts.models import StaffProfile
    from apps.equipment.models import Equipment
    eq = Equipment.objects.get(pk=equipment_id)
    admins = StaffProfile.objects.filter(
        studio=eq.studio, role__in=["owner", "manager"]
    ).select_related("user")
    for admin in admins:
        send_mail(
            f"Maintenance Due: {eq.name}",
            f"{eq.name} is due for maintenance on {eq.next_maintenance}.",
            None, [admin.user.email],
        )
