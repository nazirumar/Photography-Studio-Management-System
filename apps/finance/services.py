from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.finance.models import Invoice, InvoiceItem, Payment


def generate_next_invoice_number(studio):
    """Generate next invoice number for a studio."""
    last = Invoice.objects.filter(studio=studio).order_by("-created_at").first()
    if last and last.invoice_number:
        try:
            num = int(last.invoice_number.split("-")[-1]) + 1
        except (ValueError, IndexError):
            num = 1
    else:
        num = 1
    return f"INV-{num:04d}"


def create_invoice(studio, data, user):
    """Create an invoice with line items."""
    items_data = data.pop("items", [])
    with transaction.atomic():
        invoice_number = data.pop("invoice_number", None) or generate_next_invoice_number(studio)
        invoice = Invoice.objects.create(
            studio=studio, invoice_number=invoice_number, **data
        )
        for item_data in items_data:
            qty = item_data.get("quantity", Decimal("1"))
            price = item_data.get("unit_price", Decimal("0"))
            item_total = qty * price
            InvoiceItem.objects.create(
                invoice=invoice,
                quantity=qty,
                unit_price=price,
                total=item_total,
                **{k: v for k, v in item_data.items() if k not in ("quantity", "unit_price")},
            )
        _recalculate_invoice_totals(invoice)
        AuditLog.objects.create(
            user=user,
            action="invoice_created",
            entity_type="Invoice",
            entity_id=str(invoice.id),
            after_values={
                "invoice_number": invoice_number,
                "total": str(invoice.total),
                "client": str(invoice.client),
            },
        )
        return invoice


def _recalculate_invoice_totals(invoice):
    """Recalculate invoice totals from line items."""
    from django.db.models import Sum

    agg = invoice.items.aggregate(
        subtotal=Sum("total"),
    )
    invoice.subtotal = agg["subtotal"] or Decimal("0")
    invoice.total = invoice.subtotal - invoice.discount + invoice.tax
    invoice.balance = invoice.total - invoice.amount_paid
    if invoice.amount_paid > 0 and invoice.amount_paid < invoice.total:
        invoice.status = Invoice.Status.PARTIAL
    elif invoice.amount_paid >= invoice.total:
        invoice.status = Invoice.Status.PAID
    invoice.save(update_fields=["subtotal", "total", "balance", "status", "updated_at"])


def record_invoice_payment(invoice, amount, method, reference, user, payment_date=None):
    """Record a payment against an invoice."""
    if payment_date is None:
        payment_date = timezone.now().date()

    with transaction.atomic():
        payment = Payment.objects.create(
            studio=invoice.studio,
            client=invoice.client,
            invoice=invoice,
            amount=amount,
            method=method,
            reference=reference,
            payment_date=payment_date,
            recorded_by=user,
        )
        invoice.amount_paid += amount
        invoice.save(update_fields=["amount_paid", "updated_at"])
        _recalculate_invoice_totals(invoice)
        AuditLog.objects.create(
            user=user,
            action="invoice_payment_recorded",
            entity_type="Invoice",
            entity_id=str(invoice.id),
            after_values={"amount": str(amount), "method": method},
        )
        return payment


def void_invoice(invoice, user):
    """Void/cancel an invoice."""
    with transaction.atomic():
        old_status = invoice.status
        Invoice.objects.filter(pk=invoice.pk).update(status=Invoice.Status.CANCELLED)
        invoice.status = Invoice.Status.CANCELLED
        AuditLog.objects.create(
            user=user,
            action="invoice_voided",
            entity_type="Invoice",
            entity_id=str(invoice.id),
            before_values={"status": old_status},
            after_values={"status": "cancelled"},
        )
        return invoice


def create_invoice_from_booking(booking, user):
    """Generate an invoice from a booking's package snapshot."""
    from datetime import date

    items = []
    if booking.package:
        items.append({
            "description": f"Package: {booking.package.name}",
            "quantity": Decimal("1"),
            "unit_price": booking.base_price,
        })
    if booking.discount > 0:
        items.append({
            "description": "Discount",
            "quantity": Decimal("1"),
            "unit_price": -booking.discount,
        })
    if booking.tax > 0:
        items.append({
            "description": "Tax",
            "quantity": Decimal("1"),
            "unit_price": booking.tax,
        })

    return create_invoice(
        studio=booking.studio,
        data={
            "client": booking.client,
            "booking": booking,
            "issue_date": date.today(),
            "items": items,
            "notes": f"Auto-generated from booking {booking.reference}",
        },
        user=user,
    )


def get_revenue_summary(studio, date_from=None, date_to=None):
    """Get revenue summary for a date range."""
    from django.db.models import Sum

    qs = Payment.objects.filter(studio=studio)
    if date_from:
        qs = qs.filter(payment_date__gte=date_from)
    if date_to:
        qs = qs.filter(payment_date__lte=date_to)

    total = qs.aggregate(total=Sum("amount"))["total"] or Decimal("0")

    by_method = qs.values("method").annotate(total=Sum("amount")).order_by("method")

    return {
        "total_revenue": total,
        "by_method": list(by_method),
    }
