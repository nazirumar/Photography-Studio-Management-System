from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.bookings.models import Booking


def generate_next_reference(studio):
    """Generate next booking reference for a studio."""
    last = Booking.objects.filter(studio=studio).order_by("-created_at").first()
    if last and last.reference:
        try:
            num = int(last.reference.split("-")[-1]) + 1
        except (ValueError, IndexError):
            num = 1
    else:
        num = 1
    return f"BK-{num:05d}"


def create_booking(studio, data, user):
    """Create a booking with package price snapshot."""
    with transaction.atomic():
        reference = data.pop("reference", None) or generate_next_reference(studio)
        package = data.get("package")

        package_snapshot = {}
        if package:
            package_snapshot = {
                "name": package.name,
                "price": str(package.price),
                "deposit_percentage": str(package.deposit_percentage),
                "duration_hours": str(package.duration_hours),
                "outfit_changes": package.outfit_changes,
                "edited_images": package.edited_images,
            }

        base_price = data.pop("base_price", None)
        if base_price is None:
            base_price = package.price if package else Decimal("0.00")

        discount = data.pop("discount", Decimal("0.00"))
        tax = data.pop("tax", Decimal("0.00"))
        total_amount = data.pop("total_amount", None)
        if total_amount is None:
            total_amount = base_price - discount + tax

        deposit_required = Decimal("0.00")
        if package and package.deposit_percentage > 0:
            deposit_required = (total_amount * package.deposit_percentage / 100).quantize(
                Decimal("0.01")
            )

        booking = Booking.objects.create(
            studio=studio,
            reference=reference,
            package_snapshot=package_snapshot,
            base_price=base_price,
            discount=discount,
            tax=tax,
            total_amount=total_amount,
            deposit_required=deposit_required,
            balance=total_amount,
            created_by=user,
            **data,
        )
        AuditLog.objects.create(
            user=user,
            action="booking_created",
            entity_type="Booking",
            entity_id=str(booking.id),
            after_values={
                "reference": reference,
                "client": str(booking.client),
                "total_amount": str(total_amount),
            },
        )
        return booking


def update_booking_status(booking, new_status, user):
    """Transition booking status with validation."""
    valid_transitions = {
        Booking.Status.ENQUIRY: [
            Booking.Status.TENTATIVE,
            Booking.Status.CANCELLED,
        ],
        Booking.Status.TENTATIVE: [
            Booking.Status.AWAITING_DEPOSIT,
            Booking.Status.CONFIRMED,
            Booking.Status.CANCELLED,
        ],
        Booking.Status.AWAITING_DEPOSIT: [
            Booking.Status.CONFIRMED,
            Booking.Status.CANCELLED,
        ],
        Booking.Status.CONFIRMED: [
            Booking.Status.IN_PROGRESS,
            Booking.Status.CANCELLED,
            Booking.Status.NO_SHOW,
        ],
        Booking.Status.IN_PROGRESS: [
            Booking.Status.COMPLETED,
        ],
    }

    allowed = valid_transitions.get(booking.status, [])
    if new_status not in allowed:
        raise ValueError(
            f"Cannot transition from '{booking.status}' to '{new_status}'. "
            f"Allowed: {list(allowed)}"
        )

    with transaction.atomic():
        old_status = booking.status
        booking.status = new_status
        booking.save(update_fields=["status", "updated_at"])
        AuditLog.objects.create(
            user=user,
            action="booking_status_changed",
            entity_type="Booking",
            entity_id=str(booking.id),
            before_values={"status": old_status},
            after_values={"status": new_status},
        )
        return booking


def record_booking_payment(booking, amount, method, reference, user, payment_date=None):
    """Record a payment against a booking."""
    from apps.finance.models import Payment

    if payment_date is None:
        payment_date = timezone.now().date()

    with transaction.atomic():
        payment = Payment.objects.create(
            studio=booking.studio,
            client=booking.client,
            booking=booking,
            amount=amount,
            method=method,
            reference=reference,
            payment_date=payment_date,
            recorded_by=user,
        )
        booking.amount_paid += amount
        booking.balance = booking.total_amount - booking.amount_paid
        if booking.amount_paid >= booking.total_amount:
            booking.payment_status = Booking.PaymentStatus.PAID
        elif booking.amount_paid > 0:
            booking.payment_status = Booking.PaymentStatus.PARTIAL
        booking.save(update_fields=["amount_paid", "balance", "payment_status", "updated_at"])
        AuditLog.objects.create(
            user=user,
            action="booking_payment_recorded",
            entity_type="Booking",
            entity_id=str(booking.id),
            after_values={"amount": str(amount), "method": method, "reference": reference},
        )
        return payment
