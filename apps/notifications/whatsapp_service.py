import requests
from django.conf import settings


class WhatsAppService:
    """WhatsApp integration using the WhatsApp Business API."""

    def __init__(self):
        self.api_url = "https://graph.facebook.com/v17.0"
        self.phone_number_id = getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", "")
        self.access_token = getattr(settings, "WHATSAPP_ACCESS_TOKEN", "")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def send_message(self, phone, template_name, language="en", components=None):
        """Send a template message."""
        if not self.phone_number_id or not self.access_token:
            return {"status": False, "error": "WhatsApp not configured"}
        try:
            data = {
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": language},
                },
            }
            if components:
                data["template"]["components"] = components
            response = requests.post(
                f"{self.api_url}/{self.phone_number_id}/messages",
                headers=self._headers(),
                json=data,
                timeout=10,
            )
            return response.json()
        except Exception as e:
            return {"status": False, "error": str(e)}

    def send_text(self, phone, message):
        """Send a plain text message."""
        if not self.phone_number_id or not self.access_token:
            return {"status": False, "error": "WhatsApp not configured"}
        try:
            data = {
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "text",
                "text": {"body": message},
            }
            response = requests.post(
                f"{self.api_url}/{self.phone_number_id}/messages",
                headers=self._headers(),
                json=data,
                timeout=10,
            )
            return response.json()
        except Exception as e:
            return {"status": False, "error": str(e)}

    def send_booking_confirmation(self, booking):
        phone = booking.client.phone or booking.client.whatsapp
        if not phone:
            return {"status": False, "error": "No phone number"}
        msg = (
            f"Hi {booking.client.first_name}! Your booking *{booking.reference}* "
            f"for *{booking.date}* has been confirmed. "
            f"Package: {booking.package.name}. "
            f"Total: N{booking.total_amount:,.2f}. "
            f"Thank you for choosing {booking.studio.name}!"
        )
        return self.send_text(phone, msg)

    def send_payment_receipt(self, payment):
        phone = payment.client.phone or payment.client.whatsapp
        if not phone:
            return {"status": False, "error": "No phone number"}
        msg = (
            f"Payment received! *N{payment.amount:,.2f}* "
            f"Ref: *{payment.reference}*. "
            f"Thank you! - {payment.studio.name}"
        )
        return self.send_text(phone, msg)

    def send_invoice(self, invoice, pdf_url=""):
        phone = invoice.client.phone or invoice.client.whatsapp
        if not phone:
            return {"status": False, "error": "No phone number"}
        msg = (
            f"Hi {invoice.client.first_name}, your invoice *{invoice.invoice_number}* "
            f"for *N{invoice.total:,.2f}* is ready. "
            f"Due: {invoice.due_date}. "
            f"Balance: N{invoice.balance:,.2f}. "
        )
        if pdf_url:
            msg += f"View: {pdf_url}"
        return self.send_text(phone, msg)

    def send_delivery_notification(self, booking):
        phone = booking.client.phone or booking.client.whatsapp
        if not phone:
            return {"status": False, "error": "No phone number"}
        msg = (
            f"Hi {booking.client.first_name}! Your photos for "
            f"*{booking.reference}* are ready for delivery! "
            f"Please contact us to arrange pickup. - {booking.studio.name}"
        )
        return self.send_text(phone, msg)
