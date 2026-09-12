import logging
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, subject, text_content, html_content, recipient_list, from_email=None):
    """Send email with retry logic."""
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=recipient_list,
        )
        if html_content:
            msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Email sent successfully: {subject} to {recipient_list}")
        return {"success": True, "recipient": recipient_list}
    except Exception as exc:
        logger.error(f"Email failed: {subject} to {recipient_list}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_invoice_email_task(self, invoice_id, recipient_email=None):
    """Send invoice email with retry."""
    from apps.finance.models import Invoice
    try:
        invoice = Invoice.objects.select_related("client", "booking", "booking__studio").get(pk=invoice_id)
        studio = invoice.booking.studio if invoice.booking else invoice.project.studio
        to_email = recipient_email or invoice.client.email
        subject = f"Invoice {invoice.invoice_number} from {studio.name}"

        html_content = render_to_string("emails/invoice_email.html", {
            "invoice": invoice,
            "studio": studio,
        })
        text_content = render_to_string("emails/invoice_email.txt", {
            "invoice": invoice,
            "studio": studio,
        })

        return send_email_task.delay(subject, text_content, html_content, [to_email])
    except Exception as exc:
        logger.error(f"Failed to queue invoice email: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_receipt_email_task(self, payment_id, recipient_email=None):
    """Send payment receipt email with retry."""
    from apps.finance.models import Payment
    try:
        payment = Payment.objects.select_related("client").get(pk=payment_id)
        to_email = recipient_email or payment.client.email
        subject = f"Payment Receipt - {payment.reference}"

        html_content = render_to_string("emails/receipt_email.html", {
            "payment": payment,
        })
        text_content = render_to_string("emails/receipt_email.txt", {
            "payment": payment,
        })

        return send_email_task.delay(subject, text_content, html_content, [to_email])
    except Exception as exc:
        logger.error(f"Failed to queue receipt email: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_booking_confirmation_task(self, booking_id, recipient_email=None):
    """Send booking confirmation email with retry."""
    from apps.bookings.models import Booking
    try:
        booking = Booking.objects.select_related("client", "package").get(pk=booking_id)
        to_email = recipient_email or booking.client.email
        subject = f"Booking Confirmed - {booking.title or booking.reference}"

        html_content = render_to_string("emails/booking_confirmation.html", {
            "booking": booking,
        })
        text_content = render_to_string("emails/booking_confirmation.txt", {
            "booking": booking,
        })

        return send_email_task.delay(subject, text_content, html_content, [to_email])
    except Exception as exc:
        logger.error(f"Failed to queue booking confirmation: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_selection_ready_task(self, project_id, recipient_email=None):
    """Send selection ready email with retry."""
    from apps.projects.models import Project
    try:
        project = Project.objects.select_related("client").get(pk=project_id)
        to_email = recipient_email or project.client.email
        subject = f"Your Photos Are Ready for Selection - {project.reference}"

        html_content = render_to_string("emails/selection_ready.html", {
            "project": project,
        })
        text_content = render_to_string("emails/selection_ready.txt", {
            "project": project,
        })

        return send_email_task.delay(subject, text_content, html_content, [to_email])
    except Exception as exc:
        logger.error(f"Failed to queue selection ready email: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_delivery_notification_task(self, project_id, recipient_email=None):
    """Send delivery notification email with retry."""
    from apps.projects.models import Project
    try:
        project = Project.objects.select_related("client").get(pk=project_id)
        to_email = recipient_email or project.client.email
        subject = f"Your Photos Are Ready for Delivery - {project.reference}"

        html_content = render_to_string("emails/delivery_notification.html", {
            "project": project,
        })
        text_content = render_to_string("emails/delivery_notification.txt", {
            "project": project,
        })

        return send_email_task.delay(subject, text_content, html_content, [to_email])
    except Exception as exc:
        logger.error(f"Failed to queue delivery notification: {exc}")
        raise self.retry(exc=exc)
