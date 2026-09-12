import logging
from django.db.models import F, Sum

from apps.inventory.models import InventoryItem
from apps.notifications.models import Notification
from apps.notifications.services import create_notification
from django.utils import timezone

logger = logging.getLogger(__name__)


def check_low_stock(studio):
    """Check for low stock items and create notifications."""
    low_stock_items = InventoryItem.objects.filter(
        studio=studio,
        is_active=True,
        quantity__lte=F("reorder_level"),
    )

    for item in low_stock_items:
        exists = Notification.objects.filter(
            notification_type=Notification.Type.LOW_STOCK,
            entity_type="InventoryItem",
            entity_id=str(item.pk),
            created_at__date=timezone.now().date(),
        ).exists()

        if not exists:
            from apps.accounts.models import StaffProfile
            studio_users = [sp.user for sp in StaffProfile.objects.filter(studio=studio)]
            for user in studio_users:
                create_notification(
                    user=user,
                    title=f"Low Stock: {item.name}",
                    message=f"{item.name} has {item.quantity} {item.unit} remaining (reorder at {item.reorder_level}).",
                    notification_type=Notification.Type.LOW_STOCK,
                    entity_type="InventoryItem",
                    entity_id=str(item.pk),
                    link=f"/inventory/{item.pk}/",
                )

    return low_stock_items.count()


def get_stock_summary(studio):
    """Get stock summary for the studio."""
    items = InventoryItem.objects.filter(studio=studio, is_active=True)
    return {
        "total_items": items.count(),
        "low_stock": items.filter(quantity__lte=F("reorder_level")).count(),
        "out_of_stock": items.filter(quantity=0).count(),
        "total_value": items.aggregate(
            total=Sum(F("quantity") * F("cost_price"))
        )["total"] or 0,
    }
