from decimal import Decimal

import pytest

from apps.clients.models import Client
from apps.clients.services import (
    archive_client,
    create_client,
    generate_next_client_number,
    get_client_balance,
    get_client_lifetime_value,
    update_client,
)
from apps.finance.models import Invoice, Payment
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


@pytest.mark.django_db
class TestClientServices:
    def test_create_client(self, studio, user):
        client = create_client(
            studio,
            {
                "client_number": "CLT-001",
                "first_name": "Chidi",
                "last_name": "Okonkwo",
                "phone": "+2348012345678",
                "email": "chidi@test.com",
            },
            user,
        )
        assert client.pk is not None
        assert client.display_name == "Chidi Okonkwo"
        assert client.studio == studio

    def test_create_client_audit_log(self, studio, user):
        client = create_client(
            studio,
            {"client_number": "CLT-002", "first_name": "A", "last_name": "B"},
            user,
        )
        from apps.audit.models import AuditLog

        log = AuditLog.objects.filter(
            entity_type="Client", entity_id=str(client.pk)
        ).latest("timestamp")
        assert log.action == "client_created"

    def test_update_client(self, studio, user):
        client = create_client(
            studio,
            {"client_number": "CLT-003", "first_name": "Old", "last_name": "Name"},
            user,
        )
        updated = update_client(client, {"first_name": "New"}, user)
        assert updated.first_name == "New"
        assert updated.last_activity is not None

    def test_archive_client(self, studio, user):
        client = create_client(
            studio,
            {"client_number": "CLT-004", "first_name": "X", "last_name": "Y"},
            user,
        )
        archived = archive_client(client, user)
        assert archived.status == "archived"

    def test_generate_next_client_number_first(self, studio):
        assert generate_next_client_number(studio) == "CLT-0001"

    def test_generate_next_client_number_subsequent(self, studio, user):
        create_client(
            studio,
            {"client_number": "CLT-0005", "first_name": "A", "last_name": "B"},
            user,
        )
        assert generate_next_client_number(studio) == "CLT-0006"

    def test_get_client_balance_no_invoices(self, studio, user):
        client = create_client(
            studio,
            {"client_number": "CLT-010", "first_name": "A", "last_name": "B"},
            user,
        )
        assert get_client_balance(client) == 0

    def test_get_client_balance_with_invoices(self, studio, user):
        from datetime import date

        client = create_client(
            studio,
            {"client_number": "CLT-011", "first_name": "A", "last_name": "B"},
            user,
        )
        Invoice.objects.create(
            studio=studio,
            client=client,
            invoice_number="INV-001",
            issue_date=date.today(),
            total=Decimal("50000.00"),
            amount_paid=Decimal("20000.00"),
            status="partial",
        )
        assert get_client_balance(client) == Decimal("30000.00")

    def test_get_client_lifetime_value(self, studio, user):
        from datetime import date

        client = create_client(
            studio,
            {"client_number": "CLT-012", "first_name": "A", "last_name": "B"},
            user,
        )
        invoice = Invoice.objects.create(
            studio=studio,
            client=client,
            invoice_number="INV-002",
            issue_date=date.today(),
            total=Decimal("50000.00"),
        )
        Payment.objects.create(
            studio=studio,
            client=client,
            invoice=invoice,
            amount=Decimal("30000.00"),
            method="bank_transfer",
            reference="TXN-001",
            payment_date=date.today(),
        )
        Payment.objects.create(
            studio=studio,
            client=client,
            invoice=invoice,
            amount=Decimal("20000.00"),
            method="cash",
            reference="TXN-002",
            payment_date=date.today(),
        )
        assert get_client_lifetime_value(client) == Decimal("50000.00")

    def test_multi_tenant_isolation(self, user):
        s1 = Studio.objects.create(name="Studio A")
        s2 = Studio.objects.create(name="Studio B")
        c1 = create_client(
            s1, {"client_number": "CLT-001", "first_name": "A", "last_name": "B"}, user
        )
        create_client(
            s2, {"client_number": "CLT-001", "first_name": "C", "last_name": "D"}, user
        )
        assert Client.objects.filter(studio=s1).count() == 1
        assert Client.objects.filter(studio=s2).count() == 1
        assert Client.objects.filter(studio=s1, client_number="CLT-001").first() == c1
