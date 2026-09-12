from django.db import transaction

from apps.audit.models import AuditLog
from apps.equipment.models import Equipment


def create_equipment(studio, data, user):
    """Create a new equipment item."""
    with transaction.atomic():
        equipment = Equipment.objects.create(studio=studio, **data)
        AuditLog.objects.create(
            user=user,
            action="equipment_created",
            entity_type="Equipment",
            entity_id=str(equipment.id),
            after_values={"asset_number": equipment.asset_number, "name": equipment.name},
        )
        return equipment


def update_equipment(equipment, data, user):
    """Update an equipment item."""
    with transaction.atomic():
        before = {"status": equipment.status, "name": equipment.name}
        for key, value in data.items():
            setattr(equipment, key, value)
        equipment.save()
        AuditLog.objects.create(
            user=user,
            action="equipment_updated",
            entity_type="Equipment",
            entity_id=str(equipment.id),
            before_values=before,
            after_values={"status": equipment.status, "name": equipment.name},
        )
        return equipment


def update_equipment_status(equipment, new_status, user):
    """Update equipment status with audit."""
    with transaction.atomic():
        old_status = equipment.status
        equipment.status = new_status
        equipment.save(update_fields=["status", "updated_at"])
        AuditLog.objects.create(
            user=user,
            action="equipment_status_changed",
            entity_type="Equipment",
            entity_id=str(equipment.id),
            before_values={"status": old_status},
            after_values={"status": new_status},
        )
        return equipment


def assign_equipment(equipment, assignee, user):
    """Assign equipment to a staff member."""
    with transaction.atomic():
        equipment.assigned_to = assignee
        if assignee:
            equipment.status = Equipment.Status.IN_USE
        else:
            equipment.status = Equipment.Status.AVAILABLE
        equipment.save(update_fields=["assigned_to", "status", "updated_at"])
        AuditLog.objects.create(
            user=user,
            action="equipment_assigned",
            entity_type="Equipment",
            entity_id=str(equipment.id),
            after_values={
                "assigned_to": str(assignee) if assignee else None,
                "status": equipment.status,
            },
        )
        return equipment


def get_available_equipment(studio):
    """Get all available equipment."""
    return Equipment.objects.filter(
        studio=studio, status=Equipment.Status.AVAILABLE
    )


def get_maintenance_due(studio):
    """Get equipment due for maintenance."""
    from datetime import date

    return Equipment.objects.filter(
        studio=studio,
        next_maintenance__lte=date.today(),
        status__in=[Equipment.Status.AVAILABLE, Equipment.Status.IN_USE],
    )
