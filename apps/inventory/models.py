from django.db import models

from apps.core.models import BaseModel


class InventoryItem(BaseModel):
    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="inventory_items")
    sku = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=50, default="pcs")
    reorder_level = models.IntegerField(default=10)
    cost_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    supplier = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = [("studio", "sku")]

    def __str__(self):
        return f"{self.sku} - {self.name}"

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level

class StockTransaction(BaseModel):
    class Type(models.TextChoices):
        IN = "in", "Stock In"
        OUT = "out", "Stock Out"
        ADJUSTMENT = "adjustment", "Adjustment"
        DAMAGED = "damaged", "Damaged"
        RETURNED = "returned", "Returned"

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=20, choices=Type.choices)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, related_name="stock_transactions"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.item.name} - {self.transaction_type} - {self.quantity}"
