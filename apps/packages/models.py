from django.db import models

from apps.core.models import BaseModel


class ServiceCategory(BaseModel):
    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="service_categories")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Service categories"

    def __str__(self):
        return self.name

class Package(BaseModel):
    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="packages")
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="packages"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    deposit_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=50)
    duration_hours = models.DecimalField(max_digits=5, decimal_places=1, default=1)
    outfit_changes = models.IntegerField(default=1)
    edited_images = models.IntegerField(default=10)
    prints_included = models.IntegerField(default=0)
    print_sizes = models.JSONField(default=list, blank=True)
    frames_included = models.IntegerField(default=0)
    frame_sizes = models.JSONField(default=list, blank=True)
    album_included = models.BooleanField(default=False)
    album_specification = models.CharField(max_length=200, blank=True)
    digital_files_included = models.BooleanField(default=True)
    delivery_estimate_days = models.IntegerField(default=14)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    extra_image_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class PackageAddon(BaseModel):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="addons")
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.package.name} - {self.name}"
