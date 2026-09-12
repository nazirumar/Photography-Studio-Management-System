from decimal import Decimal

import pytest

from apps.inventory.models import InventoryItem, StockTransaction
from apps.inventory.services import (
    create_inventory_item,
    get_inventory_summary,
    get_low_stock_items,
    record_stock_transaction,
    update_inventory_item,
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
class TestInventoryServices:
    def test_create_inventory_item(self, studio, user):
        item = create_inventory_item(
            studio,
            {
                "sku": "PH-001",
                "name": "Canon 5D Mark IV",
                "category": "Cameras",
                "quantity": 5,
                "cost_price": Decimal("2500000.00"),
            },
            user,
        )
        assert item.pk is not None
        assert item.sku == "PH-001"
        assert item.quantity == 5

    def test_create_item_audit_log(self, studio, user):
        item = create_inventory_item(
            studio, {"sku": "T-001", "name": "Test"}, user
        )
        from apps.audit.models import AuditLog

        log = AuditLog.objects.filter(
            entity_type="InventoryItem", entity_id=str(item.pk)
        ).latest("timestamp")
        assert log.action == "inventory_item_created"

    def test_update_inventory_item(self, studio, user):
        item = create_inventory_item(
            studio, {"sku": "U-001", "name": "Old", "quantity": 10}, user
        )
        updated = update_inventory_item(item, {"name": "New", "quantity": 15}, user)
        assert updated.name == "New"
        assert updated.quantity == 15

    def test_record_stock_in(self, studio, user):
        item = create_inventory_item(
            studio, {"sku": "IN-001", "name": "Item", "quantity": 10}, user
        )
        txn = record_stock_transaction(
            item, StockTransaction.Type.IN, 5, user, reference="PO-001"
        )
        assert txn.pk is not None
        item.refresh_from_db()
        assert item.quantity == 15

    def test_record_stock_out(self, studio, user):
        item = create_inventory_item(
            studio, {"sku": "OUT-001", "name": "Item", "quantity": 10}, user
        )
        record_stock_transaction(item, StockTransaction.Type.OUT, 3, user)
        item.refresh_from_db()
        assert item.quantity == 7

    def test_record_stock_out_insufficient(self, studio, user):
        item = create_inventory_item(
            studio, {"sku": "FAIL-001", "name": "Item", "quantity": 2}, user
        )
        with pytest.raises(ValueError, match="Insufficient stock"):
            record_stock_transaction(item, StockTransaction.Type.OUT, 5, user)

    def test_record_stock_adjustment(self, studio, user):
        item = create_inventory_item(
            studio, {"sku": "ADJ-001", "name": "Item", "quantity": 10}, user
        )
        record_stock_transaction(item, StockTransaction.Type.ADJUSTMENT, 20, user)
        item.refresh_from_db()
        assert item.quantity == 20

    def test_record_stock_returned(self, studio, user):
        item = create_inventory_item(
            studio, {"sku": "RET-001", "name": "Item", "quantity": 5}, user
        )
        record_stock_transaction(item, StockTransaction.Type.RETURNED, 2, user)
        item.refresh_from_db()
        assert item.quantity == 7

    def test_get_low_stock_items(self, studio, user):
        create_inventory_item(
            studio, {"sku": "L-001", "name": "Low", "quantity": 3, "reorder_level": 5}, user
        )
        create_inventory_item(
            studio, {"sku": "L-002", "name": "OK", "quantity": 20, "reorder_level": 5}, user
        )
        low = get_low_stock_items(studio)
        assert low.count() == 1
        assert low.first().sku == "L-001"

    def test_get_inventory_summary(self, studio, user):
        create_inventory_item(
            studio, {"sku": "S-001", "name": "A", "quantity": 10, "cost_price": Decimal("1000")}, user
        )
        create_inventory_item(
            studio, {"sku": "S-002", "name": "B", "quantity": 5, "cost_price": Decimal("2000")}, user
        )
        summary = get_inventory_summary(studio)
        assert summary["total_items"] == 2
        assert summary["total_value"] == Decimal("20000")

    def test_multi_tenant_isolation(self, user):
        s1 = Studio.objects.create(name="Studio A")
        s2 = Studio.objects.create(name="Studio B")
        create_inventory_item(s1, {"sku": "A-001", "name": "A"}, user)
        create_inventory_item(s2, {"sku": "B-001", "name": "B"}, user)
        assert InventoryItem.objects.filter(studio=s1).count() == 1
        assert InventoryItem.objects.filter(studio=s2).count() == 1
