"""Phase 7: Financial write tools. Strongest confirmation required."""
from __future__ import annotations
import uuid
from decimal import Decimal
from datetime import date
from apps.ai_fde.tools.base import fde_tool


@fde_tool(
    name="record_payment",
    permission="finance.add_payment",
    risk="high_risk_write",
    description="Record a payment for an invoice or booking. Requires strong confirmation. Params: client_id (required), amount (required), invoice_id (optional), booking_id (optional), method (required: cash/bank_transfer/pos/card/online/other), reference (optional), notes (optional).",
)
def record_payment(context, params):
    from apps.finance.models import Invoice, Payment
    from apps.finance.services import record_invoice_payment
    from apps.clients.models import Client
    
    client_id = params.get("client_id")
    amount_str = params.get("amount")
    method = params.get("method", "cash")
    
    if not client_id or not amount_str:
        return {"success": False, "error": "client_id and amount are required"}
    
    try:
        amount = Decimal(str(amount_str))
    except (ValueError, TypeError):
        return {"success": False, "error": "Invalid amount"}
    
    if amount <= 0:
        return {"success": False, "error": "Amount must be positive"}
    
    try:
        client = Client.objects.get(pk=client_id, studio=context.studio)
    except Client.DoesNotExist:
        return {"success": False, "error": "Client not found"}
    
    valid_methods = ["cash", "bank_transfer", "pos", "card", "online", "other"]
    if method not in valid_methods:
        return {"success": False, "error": f"Invalid method. Use: {', '.join(valid_methods)}"}
    
    invoice = None
    if params.get("invoice_id"):
        try:
            invoice = Invoice.objects.get(pk=params["invoice_id"], studio=context.studio)
        except Invoice.DoesNotExist:
            return {"success": False, "error": "Invoice not found"}
    
    booking = None
    if params.get("booking_id"):
        from apps.bookings.models import Booking
        try:
            booking = Booking.objects.get(pk=params["booking_id"], studio=context.studio)
        except Booking.DoesNotExist:
            return {"success": False, "error": "Booking not found"}
    
    payment = Payment.objects.create(
        studio=context.studio,
        client=client,
        invoice=invoice,
        booking=booking,
        amount=amount,
        payment_date=date.today(),
        method=method,
        reference=params.get("reference", f"PAY-{uuid.uuid4().hex[:8].upper()}"),
        external_reference=params.get("external_reference", ""),
        notes=params.get("notes", ""),
        recorded_by=context.user,
        is_verified=True,
    )
    
    # Update invoice if linked
    if invoice:
        record_invoice_payment(
            invoice=invoice,
            amount=amount,
            method=method,
            reference=payment.reference,
            user=context.user,
        )
    
    return {
        "success": True,
        "payment_id": str(payment.pk),
        "reference": payment.reference,
        "client": client.display_name,
        "amount": str(payment.amount),
        "method": method,
        "invoice": invoice.invoice_number if invoice else None,
        "message": f"Payment of ₦{amount:,.2f} recorded for {client.display_name}",
    }


@fde_tool(
    name="refund_payment",
    permission="finance.change_payment",
    risk="high_risk_write",
    description="Create a refund for a payment. Requires strong confirmation. Params: payment_id (required), amount (optional - defaults to full payment amount), reason (required), notes (optional).",
)
def refund_payment(context, params):
    from apps.finance.models import Payment, Invoice
    
    payment_id = params.get("payment_id")
    reason = params.get("reason", "")
    
    if not payment_id:
        return {"success": False, "error": "payment_id is required"}
    if not reason:
        return {"success": False, "error": "reason is required for refunds"}
    
    try:
        original = Payment.objects.get(pk=payment_id, studio=context.studio)
    except Payment.DoesNotExist:
        return {"success": False, "error": "Payment not found"}
    
    refund_amount = original.amount
    if params.get("amount"):
        try:
            refund_amount = Decimal(str(params["amount"]))
        except (ValueError, TypeError):
            return {"success": False, "error": "Invalid amount"}
    
    if refund_amount <= 0 or refund_amount > original.amount:
        return {"success": False, "error": f"Refund amount must be between 0 and {original.amount}"}
    
    refund = Payment.objects.create(
        studio=context.studio,
        client=original.client,
        invoice=original.invoice,
        booking=original.booking,
        amount=-refund_amount,  # Negative for refund
        payment_date=date.today(),
        method=original.method,
        reference=f"REF-{uuid.uuid4().hex[:8].upper()}",
        external_reference=f"Refund of {original.reference}",
        notes=f"Refund reason: {reason}. {params.get('notes', '')}",
        recorded_by=context.user,
        is_verified=True,
    )
    
    # Update invoice balance if linked
    if original.invoice:
        inv = original.invoice
        inv.amount_paid = inv.amount_paid - refund_amount
        inv.balance = inv.total - inv.amount_paid
        if inv.balance > 0 and inv.status == "paid":
            inv.status = "partial"
        inv.save(update_fields=["amount_paid", "balance", "status", "updated_at"])
    
    return {
        "success": True,
        "payment_id": str(refund.pk),
        "reference": refund.reference,
        "original_reference": original.reference,
        "client": original.client.display_name,
        "amount": str(refund_amount),
        "message": f"Refund of ₦{refund_amount:,.2f} processed for {original.client.display_name}",
    }


@fde_tool(
    name="cancel_invoice",
    permission="finance.change_invoice",
    risk="high_risk_write",
    description="Cancel an invoice. Requires strong confirmation. Params: invoice_id (required), reason (required).",
)
def cancel_invoice(context, params):
    from apps.finance.models import Invoice
    
    invoice_id = params.get("invoice_id")
    reason = params.get("reason", "")
    
    if not invoice_id:
        return {"success": False, "error": "invoice_id is required"}
    if not reason:
        return {"success": False, "error": "reason is required to cancel an invoice"}
    
    try:
        invoice = Invoice.objects.get(pk=invoice_id, studio=context.studio)
    except Invoice.DoesNotExist:
        return {"success": False, "error": "Invoice not found"}
    
    if invoice.status == "cancelled":
        return {"success": False, "error": "Invoice is already cancelled"}
    if invoice.status == "paid":
        return {"success": False, "error": "Cannot cancel a fully paid invoice. Use refund instead."}
    
    old_status = invoice.status
    invoice.status = "cancelled"
    invoice.notes = f"{invoice.notes}\n\nCancelled: {reason}".strip()
    invoice.save(update_fields=["status", "notes", "updated_at"])
    
    return {
        "success": True,
        "invoice_id": str(invoice.pk),
        "invoice_number": invoice.invoice_number,
        "client": invoice.client.display_name,
        "old_status": old_status,
        "new_status": "cancelled",
        "amount": str(invoice.total),
        "message": f"Invoice {invoice.invoice_number} cancelled. Reason: {reason}",
    }


@fde_tool(
    name="apply_discount",
    permission="finance.change_invoice",
    risk="high_risk_write",
    description="Apply a discount to an invoice. Requires strong confirmation. Params: invoice_id (required), discount_amount (required - must be positive), reason (required).",
)
def apply_discount(context, params):
    from apps.finance.models import Invoice
    
    invoice_id = params.get("invoice_id")
    reason = params.get("reason", "")
    
    if not invoice_id:
        return {"success": False, "error": "invoice_id is required"}
    if not reason:
        return {"success": False, "error": "reason is required for discounts"}
    
    try:
        discount = Decimal(str(params.get("discount_amount", 0)))
    except (ValueError, TypeError):
        return {"success": False, "error": "Invalid discount amount"}
    
    if discount <= 0:
        return {"success": False, "error": "Discount must be positive"}
    
    try:
        invoice = Invoice.objects.get(pk=invoice_id, studio=context.studio)
    except Invoice.DoesNotExist:
        return {"success": False, "error": "Invoice not found"}
    
    if invoice.status in ("paid", "cancelled"):
        return {"success": False, "error": f"Cannot discount a {invoice.status} invoice"}
    
    if discount > invoice.subtotal:
        return {"success": False, "error": f"Discount (₦{discount:,.2f}) exceeds subtotal (₦{invoice.subtotal:,.2f})"}
    
    old_discount = invoice.discount or Decimal("0")
    old_total = invoice.total
    
    invoice.discount = old_discount + discount
    tax_rate = context.studio.tax_rate or Decimal("0")
    taxable = invoice.subtotal - invoice.discount
    invoice.tax = taxable * tax_rate / 100
    invoice.total = taxable + invoice.tax
    invoice.balance = invoice.total - invoice.amount_paid
    invoice.notes = f"{invoice.notes}\n\nDiscount applied: ₦{discount:,.2f} - {reason}".strip()
    invoice.save(update_fields=["discount", "tax", "total", "balance", "notes", "updated_at"])
    
    return {
        "success": True,
        "invoice_id": str(invoice.pk),
        "invoice_number": invoice.invoice_number,
        "discount_applied": str(discount),
        "old_total": str(old_total),
        "new_total": str(invoice.total),
        "new_balance": str(invoice.balance),
        "message": f"Discount of ₦{discount:,.2f} applied to {invoice.invoice_number}. New total: ₦{invoice.total:,.2f}",
    }