from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditLog


def generate_next_contract_number(studio):
    from apps.contracts.models import Contract
    last = Contract.objects.filter(studio=studio).order_by("-created_at").first()
    if last and last.contract_number:
        try:
            num = int(last.contract_number.split("-")[-1]) + 1
        except (ValueError, IndexError):
            num = 1
    else:
        num = 1
    return f"CTR-{num:04d}"


def create_contract(studio, booking, user, terms=None):
    """Create a contract for a booking."""
    from apps.contracts.models import Contract
    with transaction.atomic():
        contract_number = generate_next_contract_number(studio)
        contract = Contract.objects.create(
            studio=studio,
            booking=booking,
            contract_number=contract_number,
            total_amount=booking.total_amount,
            deposit_amount=booking.deposit_required,
            terms=terms or _default_terms(booking),
        )
        AuditLog.objects.create(
            studio=studio,
            user=user,
            action="contract_created",
            entity_type="Contract",
            entity_id=str(contract.pk),
            after_values={"contract_number": contract_number, "booking": booking.reference},
        )
        return contract


def send_contract(contract, user):
    """Mark contract as sent."""
    from apps.contracts.models import Contract
    with transaction.atomic():
        contract.status = Contract.Status.SENT
        contract.sent_at = timezone.now()
        contract.expires_at = timezone.now().date() + timezone.timedelta(days=14)
        contract.save(update_fields=["status", "sent_at", "expires_at", "updated_at"])
        AuditLog.objects.create(
            studio=contract.studio,
            user=user,
            action="contract_sent",
            entity_type="Contract",
            entity_id=str(contract.pk),
            after_values={"status": "sent"},
        )
        return contract


def sign_contract(contract, signature_data, signer_type="client"):
    """Record a signature on the contract."""
    from apps.contracts.models import Contract
    with transaction.atomic():
        if signer_type == "client":
            contract.client_signature = signature_data
            contract.client_signed_at = timezone.now()
        else:
            contract.studio_signature = signature_data
            contract.studio_signed_at = timezone.now()

        if contract.client_signature and contract.studio_signature:
            contract.status = Contract.Status.SIGNED

        contract.save(update_fields=[
            "client_signature", "client_signed_at",
            "studio_signature", "studio_signed_at",
            "status", "updated_at",
        ])
        return contract


def _default_terms(booking):
    return f"""PHOTOGRAPHY SERVICE AGREEMENT

1. SERVICES
The Photographer agrees to provide photography services for {booking.event_type or 'the event'} scheduled on {booking.date}.

2. PAYMENT
A deposit of ₦{booking.deposit_required:,.2f} is required to confirm the booking.
The remaining balance of ₦{booking.balance:,.2f} is due before or on the event date.

3. DELIVERY
Edited photos will be delivered within 14 business days after the event.

4. CANCELLATION
Cancellations made more than 7 days before the event will receive a full refund of the deposit.
Cancellations within 7 days of the event will forfeit the deposit.

5. COPYRIGHT
The Photographer retains copyright to all images. The client receives a license for personal use.

6. LIABILITY
The Photographer's total liability shall not exceed the total amount paid under this agreement.
"""
