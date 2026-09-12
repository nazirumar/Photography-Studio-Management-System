from datetime import date
from decimal import Decimal

import pytest

from apps.expenses.models import Expense
from apps.expenses.services import (
    create_expense,
    create_expense_category,
    delete_expense,
    get_expense_summary,
    update_expense,
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


@pytest.mark.django_db
class TestExpenseServices:
    def test_create_expense(self, studio, user):
        expense = create_expense(
            studio,
            {
                "description": "Camera lens repair",
                "amount": Decimal("25000.00"),
                "date": date.today(),
                "vendor": "PhotoTech",
            },
            user,
        )
        assert expense.pk is not None
        assert expense.reference.startswith("EXP-")
        assert expense.amount == Decimal("25000.00")

    def test_create_expense_audit_log(self, studio, user):
        expense = create_expense(
            studio,
            {"description": "Test", "amount": Decimal("1000"), "date": date.today()},
            user,
        )
        from apps.audit.models import AuditLog

        log = AuditLog.objects.filter(
            entity_type="Expense", entity_id=str(expense.pk)
        ).latest("timestamp")
        assert log.action == "expense_created"

    def test_update_expense(self, studio, user):
        expense = create_expense(
            studio,
            {"description": "Old", "amount": Decimal("1000"), "date": date.today()},
            user,
        )
        updated = update_expense(expense, {"description": "New", "amount": Decimal("2000")}, user)
        assert updated.description == "New"
        assert updated.amount == Decimal("2000")

    def test_delete_expense(self, studio, user):
        expense = create_expense(
            studio,
            {"description": "Delete me", "amount": Decimal("500"), "date": date.today()},
            user,
        )
        pk = expense.pk
        delete_expense(expense, user)
        assert not Expense.objects.filter(pk=pk).exists()

    def test_create_expense_category(self, studio, user):
        cat = create_expense_category(
            studio, {"name": "Equipment Maintenance"}, user
        )
        assert cat.pk is not None
        assert cat.name == "Equipment Maintenance"

    def test_get_expense_summary(self, studio, user):
        cat = create_expense_category(studio, {"name": "Travel"}, user)
        create_expense(
            studio,
            {"description": "Fuel", "amount": Decimal("5000"), "date": date.today(), "category": cat},
            user,
        )
        create_expense(
            studio,
            {"description": "Food", "amount": Decimal("3000"), "date": date.today(), "category": cat},
            user,
        )
        summary = get_expense_summary(studio)
        assert summary["total_expenses"] == Decimal("8000")
        assert len(summary["by_category"]) == 1

    def test_multi_tenant_isolation(self, user):
        s1 = Studio.objects.create(name="Studio A")
        s2 = Studio.objects.create(name="Studio B")
        create_expense(
            s1, {"description": "A", "amount": Decimal("1000"), "date": date.today()}, user
        )
        create_expense(
            s2, {"description": "B", "amount": Decimal("2000"), "date": date.today()}, user
        )
        assert Expense.objects.filter(studio=s1).count() == 1
        assert Expense.objects.filter(studio=s2).count() == 1
