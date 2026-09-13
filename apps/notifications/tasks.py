from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
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


@shared_task
def send_payment_reminders():
    """Check for overdue invoices and send reminders."""
    from datetime import date, timedelta
    from apps.finance.models import Invoice, PaymentReminder
    from apps.notifications.sms_service import SMSService

    today = date.today()
    sms = SMSService()

    # Find overdue invoices (issued/partial, past due_date)
    overdue_invoices = Invoice.objects.filter(
        status__in=["issued", "partial"],
        due_date__isnull=False,
        due_date__lt=today,
    ).select_related("client", "studio")

    for invoice in overdue_invoices:
        days_overdue = (today - invoice.due_date).days

        if days_overdue >= 30:
            reminder_type = PaymentReminder.ReminderType.OVERDUE_30
        elif days_overdue >= 14:
            reminder_type = PaymentReminder.ReminderType.OVERDUE_14
        elif days_overdue >= 7:
            reminder_type = PaymentReminder.ReminderType.OVERDUE_7
        else:
            continue

        if PaymentReminder.objects.filter(invoice=invoice, reminder_type=reminder_type).exists():
            continue

        # Send email
        subject = f"Payment Reminder: {invoice.invoice_number} is {days_overdue} days overdue"
        body = (
            f"Dear {invoice.client.first_name},\n\n"
            f"Your invoice {invoice.invoice_number} for ₦{invoice.balance:,.2f} "
            f"is {days_overdue} days overdue.\n\n"
            f"Please make payment as soon as possible.\n\n"
            f"Thank you,\n{invoice.studio.name}"
        )
        try:
            from django.core.mail import send_mail
            send_mail(subject, body, None, [invoice.client.email])
            sent_via = "email"
        except Exception:
            sent_via = ""

        # Send SMS if phone available
        if invoice.client.phone and sms.is_configured:
            sms_msg = (
                f"Payment Reminder: Invoice {invoice.invoice_number} "
                f"for ₦{invoice.balance:,.2f} is {days_overdue} days overdue. "
                f"Please pay now. - {invoice.studio.name}"
            )
            sms.send_sms(invoice.client.phone, sms_msg)
            sent_via = "both" if sent_via else "sms"

        PaymentReminder.objects.create(
            studio=invoice.studio,
            invoice=invoice,
            reminder_type=reminder_type,
            sent_via=sent_via or "email",
        )


@shared_task
def send_upcoming_payment_reminders():
    """Send reminders for invoices due in 7 and 3 days."""
    from datetime import date, timedelta
    from apps.finance.models import Invoice, PaymentReminder
    from apps.notifications.sms_service import SMSService
    from django.core.mail import send_mail

    today = date.today()
    sms = SMSService()

    # 7-day reminder
    due_in_7 = Invoice.objects.filter(
        status__in=["issued", "partial"],
        due_date=today + timedelta(days=7),
    ).select_related("client", "studio")

    for invoice in due_in_7:
        if not PaymentReminder.objects.filter(invoice=invoice, reminder_type="seven_day").exists():
            send_mail(
                f"Payment due in 7 days: {invoice.invoice_number}",
                f"Dear {invoice.client.first_name}, your invoice {invoice.invoice_number} "
                f"for ₦{invoice.balance:,.2f} is due on {invoice.due_date}.",
                None, [invoice.client.email],
            )
            if invoice.client.phone and sms.is_configured:
                sms.send_sms(
                    invoice.client.phone,
                    f"Reminder: {invoice.invoice_number} (₦{invoice.balance:,.2f}) due {invoice.due_date}. - {invoice.studio.name}"
                )
            PaymentReminder.objects.create(
                studio=invoice.studio, invoice=invoice,
                reminder_type="seven_day", sent_via="both" if invoice.client.phone else "email",
            )

    # 3-day reminder
    due_in_3 = Invoice.objects.filter(
        status__in=["issued", "partial"],
        due_date=today + timedelta(days=3),
    ).select_related("client", "studio")

    for invoice in due_in_3:
        if not PaymentReminder.objects.filter(invoice=invoice, reminder_type="three_day").exists():
            send_mail(
                f"Payment due in 3 days: {invoice.invoice_number}",
                f"Dear {invoice.client.first_name}, your invoice {invoice.invoice_number} "
                f"for ₦{invoice.balance:,.2f} is due on {invoice.due_date}.",
                None, [invoice.client.email],
            )
            if invoice.client.phone and sms.is_configured:
                sms.send_sms(
                    invoice.client.phone,
                    f"URGENT: {invoice.invoice_number} (₦{invoice.balance:,.2f}) due in 3 days! - {invoice.studio.name}"
                )
            PaymentReminder.objects.create(
                studio=invoice.studio, invoice=invoice,
                reminder_type="three_day", sent_via="both" if invoice.client.phone else "email",
            )


@shared_task
def check_sms_delivery_status():
    """Check delivery status of pending SMS messages."""
    from apps.notifications.models import SMSDeliveryLog
    from apps.notifications.sms_service import SMSService
    import requests

    sms = SMSService()
    if not sms.is_configured:
        return

    pending = SMSDeliveryLog.objects.filter(status="sent", termii_message_id__isnull=False)

    for log in pending:
        try:
            response = requests.get(
                f"{sms.BASE_URL}/sms/status",
                params={"api_key": sms.api_key, "message_id": log.termii_message_id},
                timeout=10,
            )
            data = response.json()
            if data.get("status") == "delivered":
                log.status = "delivered"
                log.delivered_at = timezone.now()
                log.save(update_fields=["status", "delivered_at", "updated_at"])
            elif data.get("status") == "failed":
                log.status = "failed"
                log.error_message = data.get("error", "Delivery failed")
                log.save(update_fields=["status", "error_message", "updated_at"])
        except Exception as e:
            log.error_message = str(e)
            log.save(update_fields=["error_message", "updated_at"])
