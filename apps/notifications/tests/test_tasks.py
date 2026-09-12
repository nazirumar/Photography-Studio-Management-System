from datetime import date
from decimal import Decimal

import pytest

from apps.notifications.tasks import (
    send_booking_confirmation,
    send_invoice_email,
    send_payment_receipt,
)


@pytest.mark.django_db
class TestEmailTasks:
    def _setup(self):
        from django.contrib.auth import get_user_model

        from apps.studios.models import Studio

        user_model = get_user_model()
        studio = Studio.objects.create(name="Test Studio")
        user = user_model.objects.create_user(
            email="test@studioflow.com", password="test123",
            first_name="T", last_name="U"
        )
        from apps.clients.services import create_client
        client = create_client(
            studio,
            {"client_number": "CLT-001", "first_name": "John",
             "last_name": "Doe", "email": "john@example.com"},
            user,
        )
        return studio, user, client

    def test_send_booking_confirmation(self):
        from apps.bookings.services import create_booking
        from apps.packages.services import create_package

        studio, user, client = self._setup()
        pkg = create_package(
            studio, {"name": "Basic", "price": Decimal("50000")}, user
        )
        booking = create_booking(
            studio,
            {"client": client, "package": pkg, "date": date.today(),
             "total_amount": Decimal("50000")},
            user,
        )
        result = send_booking_confirmation(str(booking.pk))
        assert result.status == "SUCCESS"

    def test_send_payment_receipt(self):
        from apps.bookings.services import create_booking
        from apps.finance.services import (
            create_invoice_from_booking,
            record_invoice_payment,
        )
        from apps.packages.services import create_package

        studio, user, client = self._setup()
        pkg = create_package(
            studio, {"name": "Basic", "price": Decimal("50000")}, user
        )
        booking = create_booking(
            studio,
            {"client": client, "package": pkg, "date": date.today(),
             "total_amount": Decimal("50000")},
            user,
        )
        invoice = create_invoice_from_booking(booking, user)
        payment = record_invoice_payment(
            invoice, Decimal("25000"), "cash", "PAY-001", user=user
        )
        result = send_payment_receipt(str(payment.pk))
        assert result.status == "SUCCESS"

    def test_send_invoice_email(self):
        from apps.bookings.services import create_booking
        from apps.finance.services import create_invoice_from_booking
        from apps.packages.services import create_package

        studio, user, client = self._setup()
        pkg = create_package(
            studio, {"name": "Basic", "price": Decimal("50000")}, user
        )
        booking = create_booking(
            studio,
            {"client": client, "package": pkg, "date": date.today(),
             "total_amount": Decimal("50000")},
            user,
        )
        invoice = create_invoice_from_booking(booking, user)
        result = send_invoice_email(str(invoice.pk))
        assert result.status == "SUCCESS"
