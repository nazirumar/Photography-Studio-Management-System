from datetime import date
from decimal import Decimal

import pytest

from apps.clients.services import create_client
from apps.reports.services import (
    get_booking_report,
    get_client_report,
    get_expense_report,
    get_financial_summary,
    get_gallery_report,
    get_lead_conversion_report,
    get_package_report,
    get_revenue_report,
)
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
        studio, {"client_number": "CLT-001", "first_name": "Test", "last_name": "Client"}, user
    )


@pytest.mark.django_db
class TestRevenueReport:
    def test_empty_revenue(self, studio):
        report = get_revenue_report(studio)
        assert report["total_revenue"] == Decimal("0")
        assert report["payment_count"] == 0

    def test_revenue_with_payments(self, studio, user, client_obj):
        from apps.bookings.services import create_booking
        from apps.finance.services import create_invoice_from_booking, record_invoice_payment
        from apps.packages.services import create_package

        pkg = create_package(studio, {"name": "Basic", "price": Decimal("50000")}, user)
        booking = create_booking(
            studio,
            {"client": client_obj, "package": pkg, "date": date.today(), "total_amount": Decimal("50000")},
            user,
        )
        invoice = create_invoice_from_booking(booking, user)
        record_invoice_payment(invoice, Decimal("50000"), "cash", "PAY-001", user=user)

        report = get_revenue_report(studio)
        assert report["total_revenue"] == Decimal("50000")


@pytest.mark.django_db
class TestExpenseReport:
    def test_empty_expense(self, studio):
        report = get_expense_report(studio)
        assert report["total_expenses"] == Decimal("0")


@pytest.mark.django_db
class TestBookingReport:
    def test_empty_booking(self, studio):
        report = get_booking_report(studio)
        assert report["total_bookings"] == 0

    def test_booking_count(self, studio, user, client_obj):
        from apps.bookings.services import create_booking
        from apps.packages.services import create_package

        pkg = create_package(studio, {"name": "Basic", "price": Decimal("50000")}, user)
        create_booking(
            studio,
            {"client": client_obj, "package": pkg, "date": date.today(), "total_amount": Decimal("50000")},
            user,
        )
        report = get_booking_report(studio)
        assert report["total_bookings"] == 1


@pytest.mark.django_db
class TestClientReport:
    def test_client_stats(self, studio, user, client_obj):
        report = get_client_report(studio)
        assert report["total_clients"] == 1


@pytest.mark.django_db
class TestLeadReport:
    def test_empty_lead(self, studio):
        report = get_lead_conversion_report(studio)
        assert report["total_leads"] == 0
        assert report["conversion_rate"] == 0


@pytest.mark.django_db
class TestPackageReport:
    def test_empty_package(self, studio):
        report = get_package_report(studio)
        assert report["popular_packages"] == []


@pytest.mark.django_db
class TestGalleryReport:
    def test_empty_gallery(self, studio):
        report = get_gallery_report(studio)
        assert report["total_photos"] == 0
        assert report["total_galleries"] == 0


@pytest.mark.django_db
class TestFinancialSummary:
    def test_empty_summary(self, studio):
        summary = get_financial_summary(studio)
        assert summary["monthly_revenue"] == Decimal("0")
        assert summary["monthly_expenses"] == Decimal("0")
        assert summary["net_profit"] == Decimal("0")
        assert summary["outstanding_invoices"] == Decimal("0")
