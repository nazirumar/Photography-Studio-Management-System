from datetime import date, time
from decimal import Decimal

import pytest

from apps.bookings.models import Booking
from apps.bookings.services import (
    create_booking,
    generate_next_reference,
    record_booking_payment,
    update_booking_status,
)
from apps.clients.services import create_client
from apps.packages.services import create_package
from apps.studios.models import Studio


@pytest.fixture
def studio(db):
    return Studio.objects.create(name="Test Studio")


@pytest.fixture
def user(db):
    from django.contrib.auth import get_user_model

    return get_user_model().objects.create_user(
        email="test@studioflow.com", password="testpass123", first_name="T", last_name="U"
    )


@pytest.fixture
def client_obj(studio, user):
    return create_client(
        studio,
        {"client_number": "CLT-001", "first_name": "Test", "last_name": "Client"},
        user,
    )


@pytest.fixture
def package_obj(studio, user):
    return create_package(
        studio,
        {
            "name": "Wedding Package",
            "price": Decimal("150000.00"),
            "deposit_percentage": Decimal("50.00"),
        },
        user,
    )


@pytest.mark.django_db
class TestBookingServices:
    def test_generate_next_reference(self, studio):
        assert generate_next_reference(studio) == "BK-00001"

    def test_generate_next_reference_subsequent(self, studio, user, client_obj):
        create_booking(
            studio,
            {"client": client_obj, "date": date.today(), "reference": "BK-00005"},
            user,
        )
        assert generate_next_reference(studio) == "BK-00006"

    def test_create_booking(self, studio, user, client_obj, package_obj):
        booking = create_booking(
            studio,
            {
                "client": client_obj,
                "package": package_obj,
                "title": "Wedding Shoot",
                "date": date(2026, 6, 15),
                "start_time": time(9, 0),
            },
            user,
        )
        assert booking.pk is not None
        assert booking.reference == "BK-00001"
        assert booking.total_amount == Decimal("150000.00")
        assert booking.deposit_required == Decimal("75000.00")
        assert booking.balance == Decimal("150000.00")
        assert booking.package_snapshot["name"] == "Wedding Package"
        assert booking.status == Booking.Status.ENQUIRY

    def test_create_booking_audit_log(self, studio, user, client_obj):
        booking = create_booking(
            studio,
            {"client": client_obj, "date": date.today()},
            user,
        )
        from apps.audit.models import AuditLog

        log = AuditLog.objects.filter(
            entity_type="Booking", entity_id=str(booking.pk)
        ).latest("timestamp")
        assert log.action == "booking_created"

    def test_update_booking_status_valid(self, studio, user, client_obj):
        booking = create_booking(
            studio,
            {"client": client_obj, "date": date.today()},
            user,
        )
        update_booking_status(booking, Booking.Status.TENTATIVE, user)
        booking.refresh_from_db()
        assert booking.status == Booking.Status.TENTATIVE

        update_booking_status(booking, Booking.Status.CONFIRMED, user)
        booking.refresh_from_db()
        assert booking.status == Booking.Status.CONFIRMED

    def test_update_booking_status_invalid(self, studio, user, client_obj):
        booking = create_booking(
            studio,
            {"client": client_obj, "date": date.today()},
            user,
        )
        with pytest.raises(ValueError, match="Cannot transition"):
            update_booking_status(booking, Booking.Status.COMPLETED, user)

    def test_record_booking_payment(self, studio, user, client_obj):
        booking = create_booking(
            studio,
            {
                "client": client_obj,
                "date": date.today(),
                "total_amount": Decimal("100000.00"),
            },
            user,
        )
        payment = record_booking_payment(
            booking=booking,
            amount=Decimal("50000.00"),
            method="bank_transfer",
            reference="TXN-001",
            user=user,
        )
        assert payment.pk is not None
        booking.refresh_from_db()
        assert booking.amount_paid == Decimal("50000.00")
        assert booking.balance == Decimal("50000.00")
        assert booking.payment_status == Booking.PaymentStatus.PARTIAL

    def test_record_full_payment(self, studio, user, client_obj):
        booking = create_booking(
            studio,
            {
                "client": client_obj,
                "date": date.today(),
                "total_amount": Decimal("100000.00"),
            },
            user,
        )
        record_booking_payment(
            booking=booking,
            amount=Decimal("100000.00"),
            method="cash",
            reference="CASH-001",
            user=user,
        )
        booking.refresh_from_db()
        assert booking.payment_status == Booking.PaymentStatus.PAID
        assert booking.balance == Decimal("0.00")

    def test_multi_tenant_isolation(self, user):
        s1 = Studio.objects.create(name="Studio A")
        s2 = Studio.objects.create(name="Studio B")
        c1 = create_client(
            s1, {"client_number": "CLT-001", "first_name": "A", "last_name": "B"}, user
        )
        c2 = create_client(
            s2, {"client_number": "CLT-001", "first_name": "C", "last_name": "D"}, user
        )
        create_booking(s1, {"client": c1, "date": date.today()}, user)
        create_booking(s2, {"client": c2, "date": date.today()}, user)
        assert Booking.objects.filter(studio=s1).count() == 1
        assert Booking.objects.filter(studio=s2).count() == 1
