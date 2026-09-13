import hashlib
import hmac
import logging
from decimal import Decimal

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger("finance.paystack")


class PaystackService:
    BASE_URL = "https://api.paystack.co"

    def __init__(self):
        self.secret_key = getattr(settings, "PAYSTACK_SECRET_KEY", "")

    @property
    def is_configured(self):
        return bool(self.secret_key)

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    def initialize_transaction(self, email, amount, reference, metadata=None):
        """Initialize a Paystack transaction and return authorization_url."""
        if not self.is_configured:
            return {"status": False, "error": "Paystack not configured"}

        try:
            payload = {
                "email": email,
                "amount": int(amount * 100),  # Paystack uses kobo
                "reference": reference,
                "currency": "NGN",
                "metadata": metadata or {},
            }
            response = requests.post(
                f"{self.BASE_URL}/transaction/initialize",
                json=payload,
                headers=self._headers(),
                timeout=15,
            )
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Paystack init error: {e}")
            return {"status": False, "error": str(e)}

    def verify_transaction(self, reference):
        """Verify a Paystack transaction by reference."""
        if not self.is_configured:
            return {"status": False, "error": "Paystack not configured"}

        try:
            response = requests.get(
                f"{self.BASE_URL}/transaction/verify/{reference}",
                headers=self._headers(),
                timeout=15,
            )
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Paystack verify error: {e}")
            return {"status": False, "error": str(e)}

    def verify_webhook(self, payload, signature):
        """Verify Paystack webhook signature."""
        secret = getattr(settings, "PAYSTACK_SECRET_KEY", "")
        computed = hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha512,
        ).hexdigest()
        return hmac.compare_digest(computed, signature)


def generate_payment_reference(invoice):
    """Generate a unique payment reference for Paystack."""
    return f"INV-{invoice.invoice_number}-{timezone.now().strftime('%Y%m%d%H%M%S')}"


def create_payment_link(invoice):
    """Generate a Paystack payment link for an invoice."""
    from apps.finance.payment_service import PaystackService
    from apps.finance.models import Payment

    service = PaystackService()
    if not service.is_configured:
        return None

    reference = generate_payment_reference(invoice)
    result = service.initialize_transaction(
        email=invoice.client.email,
        amount=invoice.balance,
        reference=reference,
        metadata={
            "invoice_id": str(invoice.pk),
            "invoice_number": invoice.invoice_number,
            "client_id": str(invoice.client.pk),
        },
    )

    if result.get("status"):
        return {
            "authorization_url": result["data"]["authorization_url"],
            "reference": reference,
        }
    return None


def handle_paystack_webhook(payload):
    """Process a Paystack webhook event."""
    from apps.finance.models import Invoice, Payment, PaymentReminder
    from apps.finance.services import _recalculate_invoice_totals

    event = payload.get("event")
    if event != "charge.success":
        return {"status": "ignored"}

    data = payload.get("data", {})
    reference = data.get("reference")
    amount = Decimal(str(data.get("amount", 0))) / 100  # Convert from kobo
    metadata = data.get("metadata", {})

    invoice_id = metadata.get("invoice_id")
    if not invoice_id:
        return {"status": "no_invoice"}

    try:
        invoice = Invoice.objects.select_related("client", "studio").get(pk=invoice_id)
    except Invoice.DoesNotExist:
        return {"status": "invoice_not_found"}

    # Check for duplicate
    if Payment.objects.filter(reference=reference).exists():
        return {"status": "already_processed"}

    with transaction.atomic():
        payment = Payment.objects.create(
            studio=invoice.studio,
            client=invoice.client,
            invoice=invoice,
            amount=amount,
            method="online",
            reference=reference,
            payment_date=timezone.now().date(),
            external_reference=data.get("id", ""),
            is_verified=True,
        )
        invoice.amount_paid += amount
        invoice.save(update_fields=["amount_paid", "updated_at"])
        _recalculate_invoice_totals(invoice)

        from apps.audit.models import AuditLog
        AuditLog.objects.create(
            studio=invoice.studio,
            action="invoice_payment_online",
            entity_type="Invoice",
            entity_id=str(invoice.pk),
            after_values={"amount": str(amount), "reference": reference},
        )

        return {"status": "success", "payment_id": str(payment.pk)}
