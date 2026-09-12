import logging

import requests
from django.conf import settings

logger = logging.getLogger("notifications.sms")


class SMSService:
    BASE_URL = "https://api.termii.com/api/v1"

    def __init__(self):
        self.api_key = getattr(settings, "TERMII_API_KEY", "")
        self.sender_id = getattr(settings, "TERMII_SENDER_ID", "StudioFlow")

    @property
    def is_configured(self):
        return bool(self.api_key)

    def send_sms(self, phone, message):
        if not self.is_configured:
            logger.warning("Termii SMS API key not configured")
            return {
                "status": False,
                "error": "SMS service not configured. Set TERMII_API_KEY in .env",
            }

        if not phone:
            return {"status": False, "error": "No phone number provided"}

        try:
            response = requests.post(
                f"{self.BASE_URL}/sms/send",
                json={
                    "api_key": self.api_key,
                    "to": phone,
                    "from": self.sender_id,
                    "sms": message,
                    "type": "plain",
                    "channel": "generic",
                },
                timeout=10,
            )
            result = response.json()
            logger.info(f"Termii SMS to {phone}: {response.status_code}")
            return result
        except requests.exceptions.ConnectionError:
            logger.error("Termii connection error")
            return {"status": False, "error": "Network error. Check your internet connection."}
        except requests.exceptions.Timeout:
            logger.error("Termii request timeout")
            return {"status": False, "error": "Request timed out. Please try again."}
        except requests.exceptions.RequestException as e:
            logger.error(f"Termii request error: {e}")
            return {"status": False, "error": "SMS service error. Please try again."}
        except ValueError:
            logger.error("Termii invalid response")
            return {"status": False, "error": "Invalid response from SMS provider."}

    def send_booking_confirmation(self, booking):
        msg = (
            f"Hi {booking.client.first_name}, your booking {booking.reference} "
            f"for {booking.date} is confirmed. - {booking.studio.name}"
        )
        return self.send_sms(booking.client.phone, msg)

    def send_payment_receipt(self, payment):
        msg = (
            f"Payment of N{payment.amount:,.2f} received. "
            f"Ref: {payment.reference}. Thank you! - {payment.studio.name}"
        )
        return self.send_sms(payment.client.phone, msg)

    def send_delivery_notification(self, booking):
        msg = (
            f"Hi {booking.client.first_name}, your photos for "
            f"{booking.reference} are ready! - {booking.studio.name}"
        )
        return self.send_sms(booking.client.phone, msg)
