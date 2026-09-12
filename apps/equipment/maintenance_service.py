import logging
from datetime import date, timedelta

from django.db.models import Q

from apps.equipment.models import Equipment
from apps.notifications.models import Notification
from apps.notifications.services import create_notification

logger = logging.getLogger(__name__)


def check_maintenance_due(studio):
    """Check for equipment due for maintenance."""
    today = date.today()
    warning_date = today + timedelta(days=7)

    due_equipment = Equipment.objects.filter(
        studio=studio,
        status__in=["available", "in_use"],
    ).filter(
        Q(next_maintenance__lte=today) |
        Q(next_maintenance__lte=warning_date, next_maintenance__gte=today)
    )

    for equipment in due_equipment:
        is_overdue = equipment.next_maintenance <= today
        exists = Notification.objects.filter(
            notification_type=Notification.Type.MAINTENANCE_DUE,
            entity_type="Equipment",
            entity_id=str(equipment.pk),
            created_at__date=today,
        ).exists()

        if not exists:
            from apps.accounts.models import StaffProfile
            studio_users = [sp.user for sp in StaffProfile.objects.filter(studio=studio)]
            for user in studio_users:
                status = "OVERDUE" if is_overdue else "due soon"
                create_notification(
                    user=user,
                    title=f"Maintenance {status}: {equipment.name}",
                    message=f"{equipment.name} ({equipment.asset_number}) maintenance is {status}. Scheduled: {equipment.next_maintenance}",
                    notification_type=Notification.Type.MAINTENANCE_DUE,
                    entity_type="Equipment",
                    entity_id=str(equipment.pk),
                    link=f"/equipment/{equipment.pk}/",
                )

    return due_equipment.count()


def get_maintenance_schedule(studio, days=30):
    """Get maintenance schedule for next N days."""
    today = date.today()
    end_date = today + timedelta(days=days)

    return Equipment.objects.filter(
        studio=studio,
        next_maintenance__gte=today,
        next_maintenance__lte=end_date,
    ).order_by("next_maintenance")


def get_overdue_maintenance(studio):
    """Get equipment with overdue maintenance."""
    today = date.today()
    return Equipment.objects.filter(
        studio=studio,
        next_maintenance__lt=today,
        status__in=["available", "in_use"],
    ).order_by("next_maintenance")


def mark_maintenance_complete(equipment, notes=""):
    """Mark equipment maintenance as complete."""
    equipment.maintenance_date = date.today()
    equipment.condition_notes = notes
    equipment.status = "available"
    equipment.save(update_fields=["maintenance_date", "condition_notes", "status", "updated_at"])
    logger.info(f"Maintenance completed for {equipment.asset_number}")
