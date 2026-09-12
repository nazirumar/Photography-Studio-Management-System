from django.db import models

from apps.core.models import BaseModel


class Currency(BaseModel):
    """Currency model for multi-currency support."""
    code = models.CharField(max_length=3, unique=True)  # NGN, USD, GBP, EUR
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)  # N, $, £, €
    exchange_rate = models.DecimalField(max_digits=14, decimal_places=6, default=1.0)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def convert_to(self, amount, target_currency):
        """Convert amount to target currency."""
        if self.code == target_currency.code:
            return amount
        # Convert to base (default) currency first, then to target
        base_amount = amount / self.exchange_rate
        return base_amount * target_currency.exchange_rate

    @classmethod
    def get_default(cls):
        """Get the default currency."""
        return cls.objects.filter(is_default=True, is_active=True).first()

    @classmethod
    def format_amount(cls, amount, currency_code=None):
        """Format amount with currency symbol."""
        if currency_code:
            currency = cls.objects.filter(code=currency_code).first()
        else:
            currency = cls.get_default()
        if currency:
            return f"{currency.symbol}{amount:,.2f}"
        return f"N{amount:,.2f}"


class ExchangeRateHistory(BaseModel):
    """Track exchange rate changes."""
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="rate_history")
    rate = models.DecimalField(max_digits=14, decimal_places=6)
    source = models.CharField(max_length=100, default="manual")

    class Meta:
        ordering = ["-created_at"]
