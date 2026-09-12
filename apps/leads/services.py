from django.db import transaction

from apps.audit.models import AuditLog
from apps.leads.models import Lead


def create_lead(studio, data, user):
    """Create a new lead."""
    with transaction.atomic():
        lead = Lead.objects.create(studio=studio, **data)
        AuditLog.objects.create(
            user=user,
            action="lead_created",
            entity_type="Lead",
            entity_id=str(lead.id),
            after_values={"name": lead.name, "status": lead.status},
        )
        return lead


def update_lead(lead, data, user):
    """Update an existing lead."""
    with transaction.atomic():
        before = {"name": lead.name, "status": lead.status}
        for key, value in data.items():
            setattr(lead, key, value)
        lead.save()
        AuditLog.objects.create(
            user=user,
            action="lead_updated",
            entity_type="Lead",
            entity_id=str(lead.id),
            before_values=before,
            after_values={"name": lead.name, "status": lead.status},
        )
        return lead


def update_lead_status(lead, new_status, user, note=""):
    """Update lead status with audit."""
    with transaction.atomic():
        old_status = lead.status
        lead.status = new_status
        lead.save(update_fields=["status", "updated_at"])
        AuditLog.objects.create(
            user=user,
            action="lead_status_changed",
            entity_type="Lead",
            entity_id=str(lead.id),
            before_values={"status": old_status},
            after_values={"status": new_status},
        )
        return lead


def convert_lead_to_client(lead, user):
    """Convert a lead to a client. Preserves lead history."""
    from apps.clients.services import create_client, generate_next_client_number

    with transaction.atomic():
        client_number = generate_next_client_number(lead.studio)
        client = create_client(
            studio=lead.studio,
            data={
                "client_number": client_number,
                "first_name": lead.name.split()[0] if lead.name else "",
                "last_name": " ".join(lead.name.split()[1:]) if lead.name and len(lead.name.split()) > 1 else "",
                "phone": lead.phone,
                "whatsapp": lead.whatsapp,
                "email": lead.email,
                "referral_source": lead.source,
                "notes": f"Converted from lead. Original notes: {lead.notes}",
            },
            user=user,
        )
        lead.converted_client = client
        lead.status = Lead.Status.WON
        lead.save(update_fields=["converted_client", "status", "updated_at"])
        AuditLog.objects.create(
            user=user,
            action="lead_converted",
            entity_type="Lead",
            entity_id=str(lead.id),
            after_values={"client_id": str(client.id), "client_number": client_number},
        )
        return client


def get_lead_pipeline_counts(studio):
    """Get lead counts by status for pipeline view."""
    from django.db.models import Count

    return Lead.objects.filter(studio=studio).values("status").annotate(count=Count("id")).order_by("status")
