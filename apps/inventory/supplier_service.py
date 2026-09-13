from decimal import Decimal
from django.db import transaction

from apps.audit.models import AuditLog


def create_supplier(studio, data, user):
    """Create a new supplier."""
    from apps.inventory.models import Supplier
    with transaction.atomic():
        supplier = Supplier.objects.create(studio=studio, **data)
        AuditLog.objects.create(
            studio=studio,
            user=user,
            action="supplier_created",
            entity_type="Supplier",
            entity_id=str(supplier.pk),
            after_values={"name": supplier.name},
        )
        return supplier


def update_supplier(supplier, data, user):
    """Update supplier details."""
    with transaction.atomic():
        for field, value in data.items():
            setattr(supplier, field, value)
        supplier.save()
        AuditLog.objects.create(
            studio=supplier.studio,
            user=user,
            action="supplier_updated",
            entity_type="Supplier",
            entity_id=str(supplier.pk),
            after_values=data,
        )
        return supplier


def generate_next_order_number(studio):
    from apps.inventory.models import SupplierOrder
    last = SupplierOrder.objects.filter(studio=studio).order_by("-created_at").first()
    if last and last.order_number:
        try:
            num = int(last.order_number.split("-")[-1]) + 1
        except (ValueError, IndexError):
            num = 1
    else:
        num = 1
    return f"SO-{num:04d}"


def create_supplier_order(studio, data, user):
    """Create an order to a supplier."""
    from apps.inventory.models import SupplierOrder
    with transaction.atomic():
        order_number = data.pop("order_number", None) or generate_next_order_number(studio)
        quantity = data.get("quantity", 1)
        unit_cost = data.get("unit_cost", Decimal("0"))
        data["total_cost"] = Decimal(str(quantity)) * Decimal(str(unit_cost))
        order = SupplierOrder.objects.create(studio=studio, order_number=order_number, ordered_by=user, **data)
        AuditLog.objects.create(
            studio=studio,
            user=user,
            action="supplier_order_created",
            entity_type="SupplierOrder",
            entity_id=str(order.pk),
            after_values={"order_number": order_number, "item": order.item_name},
        )
        return order


def receive_order(order, user):
    """Mark order as delivered and update inventory."""
    from apps.inventory.models import SupplierOrder, StockTransaction
    from django.utils import timezone

    with transaction.atomic():
        order.status = SupplierOrder.Status.DELIVERED
        order.delivered_at = timezone.now()
        order.save(update_fields=["status", "delivered_at", "updated_at"])

        if order.inventory_item:
            order.inventory_item.quantity += order.quantity
            order.inventory_item.save(update_fields=["quantity", "updated_at"])
            StockTransaction.objects.create(
                item=order.inventory_item,
                transaction_type="in",
                quantity=order.quantity,
                reference=order.order_number,
                notes=f"Received from {order.supplier.name}",
                performed_by=user,
            )
        return order
