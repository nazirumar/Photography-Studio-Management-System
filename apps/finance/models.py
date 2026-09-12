from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class Invoice(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        PARTIAL = "partial", "Partially Paid"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        CANCELLED = "cancelled", "Cancelled"

    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="invoices")
    invoice_number = models.CharField(max_length=50)
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="invoices")
    booking = models.ForeignKey(
        "bookings.Booking", on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices"
    )
    project = models.ForeignKey(
        "projects.Project", on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices"
    )
    issue_date = models.DateField(db_index=True)
    due_date = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-issue_date"]
        unique_together = [("studio", "invoice_number")]

    def __str__(self):
        return self.invoice_number

    def save(self, *args, **kwargs):
        self.balance = self.total - self.amount_paid
        # Only auto-update status if not in a terminal state
        if self.status not in [self.Status.PAID, self.Status.CANCELLED]:
            if self.amount_paid > 0 and self.amount_paid < self.total:
                self.status = self.Status.PARTIAL
            elif self.amount_paid >= self.total:
                self.status = self.Status.PAID
        super().save(*args, **kwargs)

class InvoiceItem(BaseModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    total = models.DecimalField(max_digits=14, decimal_places=2)

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.description}"

class Payment(BaseModel):
    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        POS = "pos", "POS"
        CARD = "card", "Card"
        ONLINE = "online", "Online Payment"
        OTHER = "other", "Other"

    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="payments")
    reference = models.CharField(max_length=50, unique=True)
    invoice = models.ForeignKey(
        Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments"
    )
    booking = models.ForeignKey(
        "bookings.Booking", on_delete=models.SET_NULL, null=True, blank=True, related_name="payments"
    )
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    payment_date = models.DateField(db_index=True)
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.CASH, db_index=True)
    external_reference = models.CharField(max_length=200, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="recorded_payments"
    )
    notes = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ["-payment_date"]

    def __str__(self):
        return f"{self.reference} - {self.amount}"
