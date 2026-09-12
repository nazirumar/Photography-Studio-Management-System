from __future__ import annotations

import logging
from typing import Any

from django.db.models import F, Q

from apps.inventory.models import InventoryItem

from .base import FDEContext, fde_tool

logger = logging.getLogger(__name__)


def _item_to_dict(item: InventoryItem) -> dict[str, Any]:
    return {
        "id": str(item.id),
        "sku": item.sku,
        "name": item.name,
        "category": item.category,
        "quantity": item.quantity,
        "unit": item.unit,
        "reorder_level": item.reorder_level,
        "cost_price": float(item.cost_price),
        "supplier": item.supplier,
        "location": item.location,
        "is_active": item.is_active,
        "is_low_stock": item.is_low_stock,
    }


@fde_tool(
    name="search_inventory",
    permission="inventory.view_inventoryitem",
    risk="read",
    description="Search inventory items by name, SKU, category, or supplier.",
    timeout=15,
)
def search_inventory(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        query = params.get("query", "").strip()
        limit = int(params.get("limit", 10))

        qs = InventoryItem.objects.filter(studio=context.studio, is_active=True)

        if query:
            qs = qs.filter(
                Q(name__icontains=query)
                | Q(sku__icontains=query)
                | Q(category__icontains=query)
                | Q(supplier__icontains=query)
            )

        items = list(qs[:limit])
        return {
            "success": True,
            "count": len(items),
            "items": [_item_to_dict(i) for i in items],
        }
    except Exception as exc:
        logger.exception("Error searching inventory")
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="get_inventory_item",
    permission="inventory.view_inventoryitem",
    risk="read",
    description="Get a single inventory item by ID.",
    timeout=15,
)
def get_inventory_item(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        item_id = params.get("item_id", "").strip()
        if not item_id:
            return {"success": False, "error": "item_id is required."}

        item = InventoryItem.objects.get(id=item_id, studio=context.studio)
        return {"success": True, "item": _item_to_dict(item)}
    except InventoryItem.DoesNotExist:
        return {"success": False, "error": "Inventory item not found."}
    except Exception as exc:
        logger.exception("Error getting inventory item %s", params.get("item_id"))
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="get_low_stock_items",
    permission="inventory.view_inventoryitem",
    risk="read",
    description="Get all inventory items at or below their reorder level.",
    timeout=15,
)
def get_low_stock_items(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        items = list(
            InventoryItem.objects.filter(
                studio=context.studio, is_active=True
            ).filter(quantity__lte=F("reorder_level"))
        )
        return {
            "success": True,
            "count": len(items),
            "items": [_item_to_dict(i) for i in items],
        }
    except Exception as exc:
        logger.exception("Error getting low stock items")
        return {"success": False, "error": str(exc)}
