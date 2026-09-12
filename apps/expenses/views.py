from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio
from apps.expenses.forms import ExpenseCategoryForm, ExpenseForm, ExpenseSearchForm
from apps.expenses.models import Expense, ExpenseCategory
from apps.expenses.services import (
    create_expense,
    create_expense_category,
    delete_expense,
    get_expense_summary,
    update_expense,
)


@login_required
def expense_list(request):
    studio = get_user_studio(request.user)
    form = ExpenseSearchForm(request.GET or None)
    form.fields["category"].queryset = ExpenseCategory.objects.filter(studio=studio)
    queryset = Expense.objects.filter(studio=studio).select_related("category")

    if form.is_valid():
        q = form.cleaned_data.get("q")
        category = form.cleaned_data.get("category")
        date_from = form.cleaned_data.get("date_from")
        date_to = form.cleaned_data.get("date_to")
        if q:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(reference__icontains=q)
                | Q(description__icontains=q)
                | Q(vendor__icontains=q)
            )
        if category:
            queryset = queryset.filter(category=category)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

    paginator = Paginator(queryset, 20)
    page = request.GET.get("page")
    expenses = paginator.get_page(page)

    return render(request, "expenses/list.html", {
        "expenses": expenses,
        "form": form,
        "total_count": queryset.count(),
    })


@login_required
def expense_create(request):
    studio = get_user_studio(request.user)
    if request.method == "POST":
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            create_expense(studio=studio, data=form.cleaned_data, user=request.user)
            messages.success(request, "Expense recorded.")
            return redirect("expenses:list")
    else:
        form = ExpenseForm()
    return render(request, "expenses/form.html", {"form": form, "title": "New Expense"})


@login_required
def expense_edit(request, pk):
    studio = get_user_studio(request.user)
    expense = get_object_or_404(Expense, pk=pk, studio=studio)
    if request.method == "POST":
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            update_expense(expense, form.cleaned_data, user=request.user)
            messages.success(request, "Expense updated.")
            return redirect("expenses:list")
    else:
        form = ExpenseForm(instance=expense)
    return render(request, "expenses/form.html", {"form": form, "title": "Edit Expense", "expense": expense})


@login_required
def expense_delete(request, pk):
    studio = get_user_studio(request.user)
    expense = get_object_or_404(Expense, pk=pk, studio=studio)
    if request.method == "POST":
        delete_expense(expense, user=request.user)
        messages.success(request, "Expense deleted.")
        return redirect("expenses:list")
    return render(request, "expenses/delete_confirm.html", {"expense": expense})


@login_required
def expense_category_list(request):
    studio = get_user_studio(request.user)
    categories = ExpenseCategory.objects.filter(studio=studio)
    return render(request, "expenses/category_list.html", {"categories": categories})


@login_required
def expense_category_create(request):
    studio = get_user_studio(request.user)
    if request.method == "POST":
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            create_expense_category(studio=studio, data=form.cleaned_data, user=request.user)
            messages.success(request, "Category created.")
            return redirect("expenses:categories")
    else:
        form = ExpenseCategoryForm()
    return render(request, "expenses/category_form.html", {"form": form, "title": "Add Category"})


@login_required
def expense_summary(request):
    studio = get_user_studio(request.user)
    from datetime import date
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    df = date.fromisoformat(date_from) if date_from else None
    dt = date.fromisoformat(date_to) if date_to else None
    summary = get_expense_summary(studio, date_from=df, date_to=dt)
    return render(request, "expenses/summary.html", {
        "summary": summary,
        "date_from": date_from or "",
        "date_to": date_to or "",
    })
