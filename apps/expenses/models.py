from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class ExpenseCategory(BaseModel):
    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="expense_categories")
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Expense categories"

    def __str__(self):
        return self.name

class Expense(BaseModel):
    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="expenses")
    reference = models.CharField(max_length=50)
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="expenses"
    )
    vendor = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=500)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField()
    payment_method = models.CharField(
        max_length=20,
        choices=[("cash", "Cash"), ("transfer", "Transfer"), ("pos", "POS"), ("card", "Card")],
        default="cash",
    )
    project = models.ForeignKey(
        "projects.Project", on_delete=models.SET_NULL, null=True, blank=True, related_name="expenses"
    )
    receipt = models.FileField(upload_to="receipts/", blank=True, null=True)
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="entered_expenses"
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.reference} - {self.description}"
