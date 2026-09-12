from django.db import models, transaction
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.equipment.models import Equipment
from apps.inventory.models import InventoryItem
from apps.notifications.models import Notification


def create_notification(user, title, message, notification_type=Notification.Type.GENERAL,
                        entity_type="", entity_id="", link=""):
    """Create a notification for a user."""
    with transaction.atomic():
        notif = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            entity_type=entity_type,
            entity_id=entity_id,
            link=link,
        )
        AuditLog.objects.create(
            user=user,
            action="notification_created",
            entity_type="Notification",
            entity_id=str(notif.pk),
            after_values={"title": title, "type": notification_type},
        )
        return notif


def mark_notification_read(notification):
    """Mark a notification as read."""
    notification.is_read = True
    notification.save(update_fields=["is_read", "updated_at"])
    return notification


def mark_all_read(user):
    """Mark all notifications for a user as read."""
    updated = Notification.objects.filter(user=user, is_read=False).update(is_read=True)
    return updated


def get_unread_count(user):
    """Get count of unread notifications for a user."""
    return Notification.objects.filter(user=user, is_read=False).count()


def get_notifications(user, unread_only=False, limit=50):
    """Get notifications for a user."""
    qs = Notification.objects.filter(user=user)
    if unread_only:
        qs = qs.filter(is_read=False)
    return qs[:limit]


def check_low_stock_alerts(studio):
    """Check for low stock items and create alerts."""
    low_items = InventoryItem.objects.filter(
        studio=studio, is_active=True, quantity__lte=models.F("reorder_level")
    )
    from apps.accounts.models import StaffProfile
    studio_users = [sp.user for sp in StaffProfile.objects.filter(studio=studio)]

    for item in low_items:
        for user in studio_users:
            exists = Notification.objects.filter(
                user=user,
                notification_type=Notification.Type.LOW_STOCK,
                entity_type="InventoryItem",
                entity_id=str(item.pk),
                created_at__date=timezone.now().date(),
            ).exists()
            if not exists:
                create_notification(
                    user=user,
                    title=f"Low Stock: {item.name}",
                    message=f"{item.name} is running low. Current: {item.quantity}, Reorder: {item.reorder_level}",
                    notification_type=Notification.Type.LOW_STOCK,
                    entity_type="InventoryItem",
                    entity_id=str(item.pk),
                    link=f"/inventory/{item.pk}/",
                )


def check_maintenance_due_alerts(studio):
    """Check for equipment needing maintenance."""
    from datetime import date

    equipment_due = Equipment.objects.filter(
        studio=studio, next_maintenance__lte=date.today()
    )
    from apps.accounts.models import StaffProfile
    studio_users = [sp.user for sp in StaffProfile.objects.filter(studio=studio)]

    for eq in equipment_due:
        for user in studio_users:
            exists = Notification.objects.filter(
                user=user,
                notification_type=Notification.Type.MAINTENANCE_DUE,
                entity_type="Equipment",
                entity_id=str(eq.pk),
                created_at__date=timezone.now().date(),
            ).exists()
            if not exists:
                create_notification(
                    user=user,
                    title=f"Maintenance Due: {eq.name}",
                    message=f"{eq.name} needs maintenance. Due: {eq.next_maintenance}",
                    notification_type=Notification.Type.MAINTENANCE_DUE,
                    entity_type="Equipment",
                    entity_id=str(eq.pk),
                    link=f"/equipment/{eq.pk}/",
                )


def check_booking_deadlines(studio):
    """Check for upcoming booking deadlines."""
    from datetime import timedelta

    from apps.bookings.models import Booking

    upcoming = Booking.objects.filter(
        studio=studio,
        date__lte=timezone.now().date() + timedelta(days=3),
        date__gte=timezone.now().date(),
        status__in=["confirmed", "awaiting_deposit"],
    )
    from apps.accounts.models import StaffProfile
    studio_users = [sp.user for sp in StaffProfile.objects.filter(studio=studio)]

    for booking in upcoming:
        for user in studio_users:
            exists = Notification.objects.filter(
                user=user,
                notification_type=Notification.Type.BOOKING_REMINDER,
                entity_type="Booking",
                entity_id=str(booking.pk),
                created_at__date=timezone.now().date(),
            ).exists()
            if not exists:
                days_until = (booking.date - timezone.now().date()).days
                create_notification(
                    user=user,
                    title=f"Booking in {days_until} day(s): {booking.title}",
                    message=f"Shoot on {booking.date} for {booking.client}.",
                    notification_type=Notification.Type.BOOKING_REMINDER,
                    entity_type="Booking",
                    entity_id=str(booking.pk),
                    link=f"/bookings/{booking.pk}/",
                )


def delete_old_notifications(days=90):
    """Delete notifications older than N days."""
    cutoff = timezone.now() - timezone.timedelta(days=days)
    deleted, _ = Notification.objects.filter(created_at__lt=cutoff).delete()
    return deleted
