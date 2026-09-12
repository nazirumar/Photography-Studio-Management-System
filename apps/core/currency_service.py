from decimal import Decimal

from .currency_models import Currency, ExchangeRateHistory


def convert_currency(amount, from_code, to_code):
    """Convert amount from one currency to another."""
    if from_code == to_code:
        return amount

    from_currency = Currency.objects.filter(code=from_code, is_active=True).first()
    to_currency = Currency.objects.filter(code=to_code, is_active=True).first()

    if not from_currency or not to_currency:
        return amount

    return from_currency.convert_to(Decimal(str(amount)), to_currency)


def get_exchange_rate(from_code, to_code):
    """Get exchange rate between two currencies."""
    if from_code == to_code:
        return Decimal("1.0")

    from_currency = Currency.objects.filter(code=from_code, is_active=True).first()
    to_currency = Currency.objects.filter(code=to_code, is_active=True).first()

    if not from_currency or not to_currency:
        return Decimal("1.0")

    return to_currency.exchange_rate / from_currency.exchange_rate


def update_exchange_rate(currency_code, new_rate, source="manual"):
    """Update exchange rate for a currency."""
    currency = Currency.objects.filter(code=currency_code).first()
    if currency:
        old_rate = currency.exchange_rate
        currency.exchange_rate = Decimal(str(new_rate))
        currency.save(update_fields=["exchange_rate", "updated_at"])

        ExchangeRateHistory.objects.create(
            currency=currency,
            rate=currency.exchange_rate,
            source=source,
        )
        return True
    return False


def get_all_currencies():
    """Get all active currencies."""
    return Currency.objects.filter(is_active=True).order_by("-is_default", "code")


def get_currency_choices():
    """Get currency choices for forms."""
    return [(c.code, f"{c.code} - {c.name}") for c in get_all_currencies()]
