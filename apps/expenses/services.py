from decimal import Decimal

from django.db import transaction

from apps.audit.models import AuditLog
from apps.expenses.models import Expense, ExpenseCategory


def generate_next_expense_reference(studio):
    """Generate next expense reference for a studio."""
    last = Expense.objects.filter(studio=studio).order_by("-created_at").first()
    if last and last.reference:
        try:
            num = int(last.reference.split("-")[-1]) + 1
        except (ValueError, IndexError):
            num = 1
    else:
        num = 1
    return f"EXP-{num:04d}"


def create_expense(studio, data, user):
    """Create a new expense."""
    with transaction.atomic():
        reference = data.pop("reference", None) or generate_next_expense_reference(studio)
        expense = Expense.objects.create(
            studio=studio, reference=reference, entered_by=user, **data
        )
        AuditLog.objects.create(
            user=user,
            action="expense_created",
            entity_type="Expense",
            entity_id=str(expense.id),
            after_values={
                "reference": reference,
                "amount": str(expense.amount),
                "description": expense.description,
            },
        )
        return expense


def update_expense(expense, data, user):
    """Update an expense."""
    with transaction.atomic():
        before = {"amount": str(expense.amount), "description": expense.description}
        for key, value in data.items():
            setattr(expense, key, value)
        expense.save()
        AuditLog.objects.create(
            user=user,
            action="expense_updated",
            entity_type="Expense",
            entity_id=str(expense.id),
            before_values=before,
            after_values={"amount": str(expense.amount), "description": expense.description},
        )
        return expense


def delete_expense(expense, user):
    """Delete an expense."""
    with transaction.atomic():
        AuditLog.objects.create(
            user=user,
            action="expense_deleted",
            entity_type="Expense",
            entity_id=str(expense.id),
            before_values={
                "reference": expense.reference,
                "amount": str(expense.amount),
                "description": expense.description,
            },
        )
        expense.delete()


def get_expense_summary(studio, date_from=None, date_to=None):
    """Get expense summary for a date range."""
    from django.db.models import Sum

    qs = Expense.objects.filter(studio=studio)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    total = qs.aggregate(total=Sum("amount"))["total"] or Decimal("0")

    by_category = (
        qs.filter(category__isnull=False)
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    return {
        "total_expenses": total,
        "by_category": list(by_category),
    }


def create_expense_category(studio, data, user):
    """Create a new expense category."""
    category = ExpenseCategory.objects.create(studio=studio, **data)
    AuditLog.objects.create(
        user=user,
        action="expense_category_created",
        entity_type="ExpenseCategory",
        entity_id=str(category.id),
        after_values={"name": category.name},
    )
    return category
