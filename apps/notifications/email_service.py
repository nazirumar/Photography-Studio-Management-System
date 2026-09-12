import logging
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_invoice_email(invoice, recipient_email=None):
    """Send invoice via email."""
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

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Invoice {invoice.invoice_number} sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send invoice {invoice.invoice_number}: {e}")
        return False


def send_quote_email(quote, recipient_email=None):
    """Send quote/proposal via email."""
    to_email = recipient_email or quote.client.email
    subject = f"Quote from {quote.studio.name}"

    html_content = render_to_string("emails/quote_email.html", {
        "quote": quote,
        "studio": quote.studio,
    })
    text_content = render_to_string("emails/quote_email.txt", {
        "quote": quote,
        "studio": quote.studio,
    })

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Quote sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send quote: {e}")
        return False


def send_payment_receipt(payment, recipient_email=None):
    """Send payment receipt via email."""
    to_email = recipient_email or payment.client.email
    subject = f"Payment Receipt - {payment.reference}"

    html_content = render_to_string("emails/receipt_email.html", {
        "payment": payment,
    })
    text_content = render_to_string("emails/receipt_email.txt", {
        "payment": payment,
    })

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Receipt {payment.reference} sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send receipt {payment.reference}: {e}")
        return False


def send_booking_confirmation(booking, recipient_email=None):
    """Send booking confirmation email."""
    to_email = recipient_email or booking.client.email
    subject = f"Booking Confirmed - {booking.title or booking.reference}"

    html_content = render_to_string("emails/booking_confirmation.html", {
        "booking": booking,
    })
    text_content = render_to_string("emails/booking_confirmation.txt", {
        "booking": booking,
    })

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Booking confirmation sent for {booking.reference}")
        return True
    except Exception as e:
        logger.error(f"Failed to send booking confirmation: {e}")
        return False


def send_selection_ready_email(project, recipient_email=None):
    """Send photo selection ready notification."""
    to_email = recipient_email or project.client.email
    subject = f"Your Photos Are Ready for Selection - {project.reference}"

    html_content = render_to_string("emails/selection_ready.html", {
        "project": project,
    })
    text_content = render_to_string("emails/selection_ready.txt", {
        "project": project,
    })

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Selection ready email sent for {project.reference}")
        return True
    except Exception as e:
        logger.error(f"Failed to send selection ready email: {e}")
        return False


def send_delivery_email(project, recipient_email=None):
    """Send delivery notification email."""
    to_email = recipient_email or project.client.email
    subject = f"Your Photos Are Ready for Delivery - {project.reference}"

    html_content = render_to_string("emails/delivery_notification.html", {
        "project": project,
    })
    text_content = render_to_string("emails/delivery_notification.txt", {
        "project": project,
    })

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Delivery email sent for {project.reference}")
        return True
    except Exception as e:
        logger.error(f"Failed to send delivery email: {e}")
        return False


def send_custom_email(subject, message, recipient_email, html_template=None):
    """Send a custom email."""
    try:
        if html_template:
            html_content = render_to_string(html_template, {"message": message})
            msg = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        else:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
            )
        logger.info(f"Custom email sent to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send custom email: {e}")
        return False
