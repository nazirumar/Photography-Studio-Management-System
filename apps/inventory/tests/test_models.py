import pytest
from django.contrib.auth import get_user_model

from apps.inventory.models import InventoryItem, StockTransaction
from apps.studios.models import Studio

User = get_user_model()


@pytest.mark.django_db
class TestInventoryModel:
    def test_create_item(self):
        studio = Studio.objects.create(name="Test Studio")
        item = InventoryItem.objects.create(
            studio=studio,
            sku="INV-001",
            name="Photo Paper A4",
            quantity=100,
            reorder_level=20,
        )
        assert item.sku == "INV-001"
        assert item.quantity == 100
        assert item.is_low_stock is False

    def test_low_stock(self):
        studio = Studio.objects.create(name="Test Studio")
        item = InventoryItem.objects.create(
            studio=studio, sku="INV-002", name="Ink Cartridge", quantity=5, reorder_level=10
        )
        assert item.is_low_stock is True

    def test_stock_transaction(self):
        studio = Studio.objects.create(name="Test Studio")
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        item = InventoryItem.objects.create(
            studio=studio, sku="INV-003", name="USB Drive", quantity=50
        )
        tx = StockTransaction.objects.create(
            item=item,
            transaction_type=StockTransaction.Type.OUT,
            quantity=10,
            reference="BKG-001",
            performed_by=user,
        )
        assert tx.transaction_type == "out"
        assert tx.quantity == 10
