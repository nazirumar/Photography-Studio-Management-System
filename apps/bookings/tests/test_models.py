from decimal import Decimal

import pytest
from django.utils import timezone

from apps.bookings.models import Booking
from apps.clients.models import Client
from apps.packages.models import Package
from apps.studios.models import Studio


@pytest.mark.django_db
class TestBookingModel:
    def _setup(self):
        studio = Studio.objects.create(name="Test Studio")
        client = Client.objects.create(
            studio=studio, client_number="CLT-001", first_name="Aisha", last_name="Bello"
        )
        package = Package.objects.create(
            studio=studio, name="Wedding", price=Decimal("300000.00"), deposit_percentage=Decimal("50.00")
        )
        return studio, client, package

    def test_create_booking(self):
        studio, client, package = self._setup()
        booking = Booking.objects.create(
            studio=studio,
            reference="BKG-001",
            client=client,
            package=package,
            date=timezone.now().date(),
            total_amount=Decimal("300000.00"),
            deposit_required=Decimal("150000.00"),
        )
        assert booking.reference == "BKG-001"
        assert booking.total_amount == Decimal("300000.00")
        assert booking.balance == Decimal("300000.00")

    def test_booking_save_calculates_balance(self):
        studio, client, package = self._setup()
        booking = Booking.objects.create(
            studio=studio,
            reference="BKG-002",
            client=client,
            date=timezone.now().date(),
            total_amount=Decimal("300000.00"),
            amount_paid=Decimal("100000.00"),
        )
        assert booking.balance == Decimal("200000.00")

    def test_booking_status_choices(self):
        assert Booking.Status.ENQUIRY == "enquiry"
        assert Booking.Status.CONFIRMED == "confirmed"
        assert Booking.Status.CANCELLED == "cancelled"
        assert Booking.PaymentStatus.PAID == "paid"

    def test_booking_str(self):
        studio, client, package = self._setup()
        booking = Booking.objects.create(
            studio=studio, reference="BKG-003", client=client, date=timezone.now().date()
        )
        assert "BKG-003" in str(booking)
