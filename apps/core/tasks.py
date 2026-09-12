import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def run_daily_backup():
    """Run daily automated backup."""
    from apps.core.backup_service import create_backup
    try:
        result = create_backup(name=f"auto-daily-{timezone.now().strftime('%Y%m%d')}")
        logger.info(f"Daily backup completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Daily backup failed: {e}")
        raise


@shared_task
def run_weekly_cleanup():
    """Clean up old backups (keep last 30 days)."""
    import os
    import glob
    from django.conf import settings

    backup_dir = os.path.join(settings.BASE_DIR, "backups")
    if not os.path.exists(backup_dir):
        return

    cutoff = timezone.now() - timezone.timedelta(days=30)
    deleted = 0

    for f in glob.glob(os.path.join(backup_dir, "*.json")):
        if os.path.getmtime(f) < cutoff.timestamp():
            os.remove(f)
            deleted += 1

    logger.info(f"Weekly cleanup: deleted {deleted} old backups")
    return deleted


@shared_task
def check_low_stock_alerts():
    """Periodic task to check low stock items."""
    from apps.studios.models import Studio
    from apps.inventory.alert_service import check_low_stock

    studios = Studio.objects.filter(is_active=True)
    total_alerts = 0
    for studio in studios:
        count = check_low_stock(studio)
        total_alerts += count
    return total_alerts


@shared_task
def check_maintenance_alerts():
    """Periodic task to check equipment maintenance due."""
    from apps.studios.models import Studio
    from apps.equipment.maintenance_service import check_maintenance_due

    studios = Studio.objects.filter(is_active=True)
    total_alerts = 0
    for studio in studios:
        count = check_maintenance_due(studio)
        total_alerts += count
    return total_alerts


@shared_task
def send_booking_reminders():
    """Periodic task to send booking reminders."""
    from apps.studios.models import Studio
    from apps.notifications.services import check_booking_deadlines

    studios = Studio.objects.filter(is_active=True)
    for studio in studios:
        check_booking_deadlines(studio)
