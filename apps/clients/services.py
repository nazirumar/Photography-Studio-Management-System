from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.clients.models import Client


def create_client(studio, data, user):
    """Create a new client."""
    with transaction.atomic():
        client = Client.objects.create(studio=studio, **data)
        AuditLog.objects.create(
            user=user,
            action="client_created",
            entity_type="Client",
            entity_id=str(client.id),
            after_values={"client_number": client.client_number, "name": str(client)},
        )
        return client


def update_client(client, data, user):
    """Update an existing client."""
    with transaction.atomic():
        before = {"name": str(client), "email": client.email, "phone": client.phone}
        for key, value in data.items():
            setattr(client, key, value)
        client.last_activity = timezone.now()
        client.save()
        AuditLog.objects.create(
            user=user,
            action="client_updated",
            entity_type="Client",
            entity_id=str(client.id),
            before_values=before,
            after_values={"name": str(client), "email": client.email, "phone": client.phone},
        )
        return client


def archive_client(client, user):
    """Soft-delete/archive a client."""
    with transaction.atomic():
        client.status = "archived"
        client.save(update_fields=["status", "updated_at"])
        AuditLog.objects.create(
            user=user,
            action="client_archived",
            entity_type="Client",
            entity_id=str(client.id),
            after_values={"status": "archived"},
        )
        return client


def get_client_balance(client):
    """Calculate total outstanding balance across all invoices."""
    from django.db.models import Sum

    from apps.finance.models import Invoice

    result = Invoice.objects.filter(client=client, status__in=["issued", "partial", "overdue"]).aggregate(
        total=Sum("total"),
        paid=Sum("amount_paid"),
    )
    total = result["total"] or 0
    paid = result["paid"] or 0
    return total - paid


def get_client_lifetime_value(client):
    """Calculate total payments received from a client."""
    from django.db.models import Sum

    from apps.finance.models import Payment

    return Payment.objects.filter(client=client).aggregate(total=Sum("amount"))["total"] or 0


def generate_next_client_number(studio):
    """Generate the next client number for a studio."""
    last = Client.objects.filter(studio=studio).order_by("-created_at").first()
    if last and last.client_number:
        try:
            num = int(last.client_number.split("-")[-1]) + 1
        except (ValueError, IndexError):
            num = 1
    else:
        num = 1
    return f"CLT-{num:04d}"
