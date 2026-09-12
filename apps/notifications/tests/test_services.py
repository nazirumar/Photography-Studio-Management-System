from datetime import date, timedelta
from decimal import Decimal

import pytest

from apps.notifications.models import Notification
from apps.notifications.services import (
    check_low_stock_alerts,
    check_maintenance_due_alerts,
    create_notification,
    delete_old_notifications,
    get_notifications,
    get_unread_count,
    mark_all_read,
    mark_notification_read,
)
from apps.studios.models import Studio


@pytest.fixture
def studio(db):
    return Studio.objects.create(name="Test Studio")


@pytest.fixture
def user(db):
    from django.contrib.auth import get_user_model
    return get_user_model().objects.create_user(
        email="test@studioflow.com", password="testpass123", first_name="T", last_name="U"
    )


@pytest.mark.django_db
class TestNotificationCreation:
    def test_create_notification(self, user):
        notif = create_notification(user, "Test", "Test message")
        assert notif.pk is not None
        assert notif.title == "Test"
        assert notif.is_read is False

    def test_create_notification_with_type(self, user):
        notif = create_notification(user, "Payment", "Received", notification_type=Notification.Type.PAYMENT_RECEIVED)
        assert notif.notification_type == Notification.Type.PAYMENT_RECEIVED

    def test_create_notification_with_entity(self, user):
        notif = create_notification(
            user, "Low Stock", "Item low",
            entity_type="InventoryItem", entity_id="abc-123", link="/inventory/abc-123/"
        )
        assert notif.entity_type == "InventoryItem"
        assert notif.entity_id == "abc-123"
        assert notif.link == "/inventory/abc-123/"

    def test_create_notification_audit_log(self, user):
        notif = create_notification(user, "Test", "msg")
        from apps.audit.models import AuditLog
        log = AuditLog.objects.filter(
            entity_type="Notification", entity_id=str(notif.pk)
        ).latest("timestamp")
        assert log.action == "notification_created"


@pytest.mark.django_db
class TestNotificationRead:
    def test_mark_read(self, user):
        notif = create_notification(user, "Test", "msg")
        mark_notification_read(notif)
        notif.refresh_from_db()
        assert notif.is_read is True

    def test_mark_all_read(self, user):
        create_notification(user, "N1", "m1")
        create_notification(user, "N2", "m2")
        create_notification(user, "N3", "m3")
        updated = mark_all_read(user)
        assert updated == 3
        assert Notification.objects.filter(user=user, is_read=False).count() == 0

    def test_get_unread_count(self, user):
        create_notification(user, "N1", "m1")
        create_notification(user, "N2", "m2")
        assert get_unread_count(user) == 2
        mark_all_read(user)
        assert get_unread_count(user) == 0


@pytest.mark.django_db
class TestNotificationRetrieval:
    def test_get_notifications(self, user):
        create_notification(user, "N1", "m1")
        create_notification(user, "N2", "m2")
        notifs = get_notifications(user)
        assert notifs.count() == 2

    def test_get_notifications_unread_only(self, user):
        n1 = create_notification(user, "N1", "m1")
        create_notification(user, "N2", "m2")
        mark_notification_read(n1)
        notifs = get_notifications(user, unread_only=True)
        assert notifs.count() == 1

    def test_get_notifications_limit(self, user):
        for i in range(5):
            create_notification(user, f"N{i}", f"m{i}")
        notifs = get_notifications(user, limit=3)
        assert notifs.count() == 3


@pytest.mark.django_db
class TestLowStockAlerts:
    def test_creates_alerts_for_low_stock(self, user, studio):
        from apps.accounts.models import StaffProfile
        from apps.inventory.models import InventoryItem
        StaffProfile.objects.create(user=user, studio=studio, role="admin")
        item = InventoryItem.objects.create(
            studio=studio, name="Photo Paper", sku="PP-001",
            quantity=2, reorder_level=5, cost_price=Decimal("8.00")
        )
        check_low_stock_alerts(studio)
        assert Notification.objects.filter(
            user=user, notification_type=Notification.Type.LOW_STOCK,
            entity_type="InventoryItem", entity_id=str(item.pk)
        ).count() == 1

    def test_no_duplicate_alerts_same_day(self, user, studio):
        from apps.accounts.models import StaffProfile
        from apps.inventory.models import InventoryItem
        StaffProfile.objects.create(user=user, studio=studio, role="admin")
        item = InventoryItem.objects.create(
            studio=studio, name="Paper", sku="PP-001",
            quantity=1, reorder_level=5, cost_price=Decimal("8.00")
        )
        check_low_stock_alerts(studio)
        check_low_stock_alerts(studio)
        assert Notification.objects.filter(
            entity_type="InventoryItem", entity_id=str(item.pk)
        ).count() == 1


@pytest.mark.django_db
class TestMaintenanceAlerts:
    def test_creates_alerts_for_due_maintenance(self, user, studio):
        from apps.accounts.models import StaffProfile
        from apps.equipment.models import Equipment
        StaffProfile.objects.create(user=user, studio=studio, role="admin")
        eq = Equipment.objects.create(
            studio=studio, name="Camera", asset_number="CAM-001",
            next_maintenance=date.today()
        )
        check_maintenance_due_alerts(studio)
        assert Notification.objects.filter(
            user=user, notification_type=Notification.Type.MAINTENANCE_DUE,
            entity_type="Equipment", entity_id=str(eq.pk)
        ).count() == 1


@pytest.mark.django_db
class TestCleanup:
    def test_delete_old_notifications(self, user):
        from django.utils import timezone
        notif = create_notification(user, "Old", "msg")
        Notification.objects.filter(pk=notif.pk).update(
            created_at=timezone.now() - timedelta(days=100)
        )
        deleted = delete_old_notifications(days=90)
        assert deleted == 1

    def test_keep_recent_notifications(self, user):
        notif = create_notification(user, "Recent", "msg")
        deleted = delete_old_notifications(days=90)
        assert deleted == 0
        assert Notification.objects.filter(pk=notif.pk).exists()
