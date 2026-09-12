import uuid

from django.db import models


class Studio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Nigeria")
    currency = models.CharField(max_length=3, default="NGN")
    timezone = models.CharField(max_length=50, default="Africa/Lagos")
    invoice_prefix = models.CharField(max_length=10, default="INV")
    receipt_prefix = models.CharField(max_length=10, default="RCT")
    booking_prefix = models.CharField(max_length=10, default="BKG")
    project_prefix = models.CharField(max_length=10, default="PRJ")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    default_deposit_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=50)
    default_payment_terms = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
