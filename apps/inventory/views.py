from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio
from apps.inventory.forms import InventoryItemForm, InventorySearchForm, StockTransactionForm
from apps.inventory.models import InventoryItem
from apps.inventory.services import (
    create_inventory_item,
    get_inventory_summary,
    get_low_stock_items,
    record_stock_transaction,
    update_inventory_item,
)


@login_required
def inventory_list(request):
    studio = get_user_studio(request.user)
    form = InventorySearchForm(request.GET or None)
    queryset = InventoryItem.objects.filter(studio=studio)

    if form.is_valid():
        q = form.cleaned_data.get("q")
        category = form.cleaned_data.get("category")
        low_stock = form.cleaned_data.get("low_stock")
        if q:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(sku__icontains=q) | Q(supplier__icontains=q)
            )
        if category:
            queryset = queryset.filter(category__icontains=category)
        if low_stock:
            from django.db.models import F
            queryset = queryset.filter(quantity__lte=F("reorder_level"))

    paginator = Paginator(queryset, 20)
    page = request.GET.get("page")
    items = paginator.get_page(page)
    summary = get_inventory_summary(studio)

    return render(request, "inventory/list.html", {
        "items": items,
        "form": form,
        "total_count": queryset.count(),
        "summary": summary,
    })


@login_required
def inventory_create(request):
    studio = get_user_studio(request.user)
    if request.method == "POST":
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            create_inventory_item(studio=studio, data=form.cleaned_data, user=request.user)
            messages.success(request, "Item created.")
            return redirect("inventory:list")
    else:
        form = InventoryItemForm()
    return render(request, "inventory/form.html", {"form": form, "title": "Add Item"})


@login_required
def inventory_detail(request, pk):
    studio = get_user_studio(request.user)
    item = get_object_or_404(
        InventoryItem.objects.prefetch_related("transactions__performed_by"),
        pk=pk, studio=studio,
    )
    transactions = item.transactions.all()[:20]
    transaction_form = StockTransactionForm()
    return render(request, "inventory/detail.html", {
        "item": item,
        "transactions": transactions,
        "transaction_form": transaction_form,
    })


@login_required
def inventory_edit(request, pk):
    studio = get_user_studio(request.user)
    item = get_object_or_404(InventoryItem, pk=pk, studio=studio)
    if request.method == "POST":
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            update_inventory_item(item, form.cleaned_data, user=request.user)
            messages.success(request, "Item updated.")
            return redirect("inventory:detail", pk=item.pk)
    else:
        form = InventoryItemForm(instance=item)
    return render(request, "inventory/form.html", {"form": form, "title": "Edit Item", "item": item})


@login_required
def inventory_transaction(request, pk):
    studio = get_user_studio(request.user)
    item = get_object_or_404(InventoryItem, pk=pk, studio=studio)
    if request.method == "POST":
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                record_stock_transaction(
                    item=item,
                    transaction_type=cd["transaction_type"],
                    quantity=cd["quantity"],
                    user=request.user,
                    reference=cd.get("reference", ""),
                    notes=cd.get("notes", ""),
                )
                messages.success(request, f"Stock {cd['transaction_type']} recorded.")
            except ValueError as e:
                messages.error(request, str(e))
    return redirect("inventory:detail", pk=pk)


@login_required
def low_stock_list(request):
    studio = get_user_studio(request.user)
    items = get_low_stock_items(studio)
    return render(request, "inventory/low_stock.html", {"items": items})
