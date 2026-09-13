"""
Email marketing integration module.
Supports Brevo (formerly Sendinblue) API.
"""
import logging

from django.conf import settings

logger = logging.getLogger("integrations.email_marketing")


class BrevoService:
    """Brevo email marketing integration."""

    BASE_URL = "https://api.brevo.com/v3"

    def __init__(self):
        self.api_key = getattr(settings, "BREVO_API_KEY", "")

    @property
    def is_configured(self):
        return bool(self.api_key)

    def _headers(self):
        return {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def add_contact(self, email, first_name="", last_name="", list_id=None):
        """Add a contact to Brevo."""
        if not self.is_configured:
            return {"status": False, "error": "Brevo not configured"}

        import requests
        try:
            payload = {
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
            }
            if list_id:
                payload["listIds"] = [list_id]

            response = requests.post(
                f"{self.BASE_URL}/contacts",
                json=payload,
                headers=self._headers(),
                timeout=10,
            )
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Brevo add contact error: {e}")
            return {"status": False, "error": str(e)}

    def send_campaign(self, subject, html_content, list_id, sender_name="StudioFlow"):
        """Send an email campaign to a list."""
        if not self.is_configured:
            return {"status": False, "error": "Brevo not configured"}

        import requests
        try:
            default_email = getattr(
                settings, "DEFAULT_FROM_EMAIL", "noreply@studioflow.com"
            )
            payload = {
                "sender": {"name": sender_name, "email": default_email},
                "subject": subject,
                "htmlContent": html_content,
                "toList": [{"id": list_id}],
            }
            response = requests.post(
                f"{self.BASE_URL}/emailCampaigns",
                json=payload,
                headers=self._headers(),
                timeout=15,
            )
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Brevo send campaign error: {e}")
            return {"status": False, "error": str(e)}

    def get_lists(self):
        """Get all contact lists."""
        if not self.is_configured:
            return []

        import requests
        try:
            response = requests.get(
                f"{self.BASE_URL}/lists",
                headers=self._headers(),
                timeout=10,
            )
            data = response.json()
            return data.get("lists", [])
        except requests.RequestException:
            return []


class MailchimpService:
    """Mailchimp email marketing integration."""

    def __init__(self):
        self.api_key = getattr(settings, "MAILCHIMP_API_KEY", "")
        self.server = self.api_key.split("-")[-1] if self.api_key else ""

    @property
    def is_configured(self):
        return bool(self.api_key)

    def add_member(self, email, first_name="", last_name="", list_id=None):
        """Add a member to a Mailchimp list."""
        if not self.is_configured:
            return {"status": False, "error": "Mailchimp not configured"}

        import requests
        try:
            payload = {
                "email_address": email,
                "status": "subscribed",
                "merge_fields": {
                    "FNAME": first_name,
                    "LNAME": last_name,
                },
            }
            response = requests.post(
                f"https://{self.server}.api.mailchimp.com/3.0/lists/{list_id}/members",
                json=payload,
                auth=("anystring", self.api_key),
                timeout=10,
            )
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Mailchimp add member error: {e}")
            return {"status": False, "error": str(e)}


def get_email_marketing_service():
    """Get the configured email marketing service."""
    if getattr(settings, "BREVO_API_KEY", ""):
        return BrevoService()
    if getattr(settings, "MAILCHIMP_API_KEY", ""):
        return MailchimpService()
    return None
