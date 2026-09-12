from datetime import date
from decimal import Decimal

import pytest

from apps.clients.services import create_client
from apps.finance.models import Invoice
from apps.finance.services import (
    create_invoice,
    get_revenue_summary,
    record_invoice_payment,
    void_invoice,
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
        studio,
        {"client_number": "CLT-001", "first_name": "Test", "last_name": "Client"},
        user,
    )


@pytest.mark.django_db
class TestInvoiceServices:
    def test_create_invoice(self, studio, user, client_obj):
        invoice = create_invoice(
            studio,
            {
                "client": client_obj,
                "issue_date": date.today(),
                "items": [
                    {"description": "Wedding package", "quantity": Decimal("1"), "unit_price": Decimal("150000.00")},
                    {"description": "Extra prints", "quantity": Decimal("5"), "unit_price": Decimal("2000.00")},
                ],
            },
            user,
        )
        assert invoice.pk is not None
        assert invoice.invoice_number.startswith("INV-")
        assert invoice.total == Decimal("160000.00")
        assert invoice.items.count() == 2

    def test_create_invoice_audit_log(self, studio, user, client_obj):
        invoice = create_invoice(
            studio,
            {"client": client_obj, "issue_date": date.today(), "items": []},
            user,
        )
        from apps.audit.models import AuditLog

        log = AuditLog.objects.filter(
            entity_type="Invoice", entity_id=str(invoice.pk)
        ).latest("timestamp")
        assert log.action == "invoice_created"

    def test_record_invoice_payment(self, studio, user, client_obj):
        invoice = create_invoice(
            studio,
            {
                "client": client_obj,
                "issue_date": date.today(),
                "items": [{"description": "Service", "unit_price": Decimal("50000.00")}],
            },
            user,
        )
        payment = record_invoice_payment(
            invoice, Decimal("20000.00"), "bank_transfer", "TXN-001", user
        )
        assert payment.pk is not None
        invoice.refresh_from_db()
        assert invoice.amount_paid == Decimal("20000.00")
        assert invoice.balance == Decimal("30000.00")
        assert invoice.status == Invoice.Status.PARTIAL

    def test_record_full_payment(self, studio, user, client_obj):
        invoice = create_invoice(
            studio,
            {
                "client": client_obj,
                "issue_date": date.today(),
                "items": [{"description": "Service", "unit_price": Decimal("50000.00")}],
            },
            user,
        )
        record_invoice_payment(
            invoice, Decimal("50000.00"), "cash", "CASH-001", user
        )
        invoice.refresh_from_db()
        assert invoice.status == Invoice.Status.PAID
        assert invoice.balance == Decimal("0.00")

    def test_void_invoice(self, studio, user, client_obj):
        invoice = create_invoice(
            studio,
            {"client": client_obj, "issue_date": date.today(), "items": []},
            user,
        )
        void_invoice(invoice, user)
        invoice.refresh_from_db()
        assert invoice.status == Invoice.Status.CANCELLED

    def test_get_revenue_summary(self, studio, user, client_obj):
        invoice = create_invoice(
            studio,
            {
                "client": client_obj,
                "issue_date": date.today(),
                "items": [{"description": "S", "unit_price": Decimal("100000.00")}],
            },
            user,
        )
        record_invoice_payment(invoice, Decimal("60000.00"), "bank_transfer", "T1", user)
        record_invoice_payment(invoice, Decimal("40000.00"), "cash", "T2", user)
        summary = get_revenue_summary(studio)
        assert summary["total_revenue"] == Decimal("100000.00")
        assert len(summary["by_method"]) == 2

    def test_multi_tenant_isolation(self, user):
        s1 = Studio.objects.create(name="Studio A")
        s2 = Studio.objects.create(name="Studio B")
        c1 = create_client(
            s1, {"client_number": "CLT-001", "first_name": "A", "last_name": "B"}, user
        )
        c2 = create_client(
            s2, {"client_number": "CLT-001", "first_name": "C", "last_name": "D"}, user
        )
        create_invoice(
            s1, {"client": c1, "issue_date": date.today(), "items": []}, user
        )
        create_invoice(
            s2, {"client": c2, "issue_date": date.today(), "items": []}, user
        )
        assert Invoice.objects.filter(studio=s1).count() == 1
        assert Invoice.objects.filter(studio=s2).count() == 1
