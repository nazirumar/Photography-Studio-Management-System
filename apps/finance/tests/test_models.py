from decimal import Decimal

import pytest
from django.utils import timezone

from apps.clients.models import Client
from apps.finance.models import Invoice, Payment
from apps.studios.models import Studio


@pytest.mark.django_db
class TestInvoiceModel:
    def _setup(self):
        studio = Studio.objects.create(name="Test Studio")
        client = Client.objects.create(
            studio=studio, client_number="CLT-001", first_name="Test", last_name="Client"
        )
        return studio, client

    def test_create_invoice(self):
        studio, client = self._setup()
        invoice = Invoice.objects.create(
            studio=studio,
            invoice_number="INV-001",
            client=client,
            issue_date=timezone.now().date(),
            subtotal=Decimal("300000.00"),
            total=Decimal("300000.00"),
        )
        assert invoice.invoice_number == "INV-001"
        assert invoice.total == Decimal("300000.00")
        assert invoice.balance == Decimal("300000.00")
        assert invoice.status == Invoice.Status.DRAFT

    def test_invoice_save_calculates_balance(self):
        studio, client = self._setup()
        invoice = Invoice.objects.create(
            studio=studio,
            invoice_number="INV-002",
            client=client,
            issue_date=timezone.now().date(),
            total=Decimal("300000.00"),
            amount_paid=Decimal("100000.00"),
        )
        assert invoice.balance == Decimal("200000.00")
        assert invoice.status == Invoice.Status.PARTIAL

    def test_invoice_fully_paid(self):
        studio, client = self._setup()
        invoice = Invoice.objects.create(
            studio=studio,
            invoice_number="INV-003",
            client=client,
            issue_date=timezone.now().date(),
            total=Decimal("100000.00"),
            amount_paid=Decimal("100000.00"),
        )
        assert invoice.balance == Decimal("0.00")
        assert invoice.status == Invoice.Status.PAID

    def test_create_payment(self):
        studio, client = self._setup()
        invoice = Invoice.objects.create(
            studio=studio,
            invoice_number="INV-004",
            client=client,
            issue_date=timezone.now().date(),
            total=Decimal("200000.00"),
        )
        payment = Payment.objects.create(
            studio=studio,
            reference="PAY-001",
            invoice=invoice,
            client=client,
            amount=Decimal("100000.00"),
            payment_date=timezone.now().date(),
            method=Payment.Method.BANK_TRANSFER,
        )
        assert payment.amount == Decimal("100000.00")
        assert payment.method == Payment.Method.BANK_TRANSFER
