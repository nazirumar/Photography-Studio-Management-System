from decimal import Decimal

from django.db import transaction

from apps.audit.models import AuditLog
from apps.inventory.models import InventoryItem, StockTransaction


def create_inventory_item(studio, data, user):
    """Create a new inventory item."""
    with transaction.atomic():
        item = InventoryItem.objects.create(studio=studio, **data)
        AuditLog.objects.create(
            user=user,
            action="inventory_item_created",
            entity_type="InventoryItem",
            entity_id=str(item.id),
            after_values={"sku": item.sku, "name": item.name},
        )
        return item


def update_inventory_item(item, data, user):
    """Update an inventory item."""
    with transaction.atomic():
        before = {"name": item.name, "quantity": item.quantity}
        for key, value in data.items():
            setattr(item, key, value)
        item.save()
        AuditLog.objects.create(
            user=user,
            action="inventory_item_updated",
            entity_type="InventoryItem",
            entity_id=str(item.id),
            before_values=before,
            after_values={"name": item.name, "quantity": item.quantity},
        )
        return item


def record_stock_transaction(item, transaction_type, quantity, user, reference="", notes=""):
    """Record a stock transaction and update item quantity."""
    with transaction.atomic():
        if transaction_type == StockTransaction.Type.IN:
            item.quantity += quantity
        elif transaction_type == StockTransaction.Type.OUT:
            if item.quantity < quantity:
                raise ValueError(f"Insufficient stock. Available: {item.quantity}, requested: {quantity}")
            item.quantity -= quantity
        elif transaction_type == StockTransaction.Type.RETURNED:
            item.quantity += quantity
        elif transaction_type == StockTransaction.Type.DAMAGED:
            if item.quantity < quantity:
                raise ValueError(f"Insufficient stock. Available: {item.quantity}, requested: {quantity}")
            item.quantity -= quantity
        elif transaction_type == StockTransaction.Type.ADJUSTMENT:
            item.quantity = quantity

        item.save(update_fields=["quantity", "updated_at"])

        transaction_obj = StockTransaction.objects.create(
            item=item,
            transaction_type=transaction_type,
            quantity=quantity,
            reference=reference,
            notes=notes,
            performed_by=user,
        )
        AuditLog.objects.create(
            user=user,
            action="stock_transaction",
            entity_type="StockTransaction",
            entity_id=str(transaction_obj.id),
            after_values={
                "item": item.name,
                "type": transaction_type,
                "quantity": quantity,
                "new_balance": item.quantity,
            },
        )
        return transaction_obj


def get_low_stock_items(studio):
    """Get all items at or below reorder level."""
    from django.db.models import F

    return InventoryItem.objects.filter(
        studio=studio, is_active=True, quantity__lte=F("reorder_level")
    )


def get_inventory_summary(studio):
    """Get inventory summary statistics."""
    from django.db.models import Sum

    items = InventoryItem.objects.filter(studio=studio, is_active=True)
    total_items = items.count()
    total_value = items.aggregate(
        total=Sum(Decimal(str(1)) * Decimal(str(0)))
    )["total"] or Decimal("0")
    # Calculate value manually since F() expressions don't work well with Decimal multiplication in SQLite
    total_value = sum(item.quantity * item.cost_price for item in items)
    low_stock = items.filter(quantity__lte=10).count()

    return {
        "total_items": total_items,
        "total_value": total_value,
        "low_stock_count": low_stock,
    }
