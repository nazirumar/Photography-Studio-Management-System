from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class Equipment(BaseModel):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        IN_USE = "in_use", "In Use"
        RESERVED = "reserved", "Reserved"
        MAINTENANCE = "maintenance", "Maintenance"
        DAMAGED = "damaged", "Damaged"
        RETIRED = "retired", "Retired"

    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="equipment")
    asset_number = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100, blank=True)
    model_name = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=200, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_equipment",
    )
    condition_notes = models.TextField(blank=True)
    maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = [("studio", "asset_number")]

    def __str__(self):
        return f"{self.asset_number} - {self.name}"


class MaintenanceLog(BaseModel):
    """Record of equipment maintenance activities."""

    class MaintenanceType(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        REPAIR = "repair", "Repair"
        INSPECTION = "inspection", "Inspection"
        CALIBRATION = "calibration", "Calibration"
        CLEANING = "cleaning", "Cleaning"
        OTHER = "other", "Other"

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="maintenance_logs")
    maintenance_type = models.CharField(max_length=20, choices=MaintenanceType.choices, default=MaintenanceType.SCHEDULED)
    description = models.TextField()
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="maintenance_performed",
    )
    vendor = models.CharField(max_length=200, blank=True)
    cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    performed_date = models.DateField()
    next_due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta(BaseModel.Meta):
        ordering = ["-performed_date"]

    def __str__(self):
        return f"Maintenance: {self.equipment.name} on {self.performed_date}"
