from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio


@login_required
def supplier_list(request):
    """List all suppliers."""
    studio = get_user_studio(request.user)
    from apps.inventory.models import Supplier
    suppliers = Supplier.objects.filter(studio=studio)

    search = request.GET.get("q", "")
    if search:
        from django.db.models import Q
        suppliers = suppliers.filter(Q(name__icontains=search) | Q(contact_person__icontains=search))

    paginator = Paginator(suppliers, 20)
    page = request.GET.get("page")
    suppliers_page = paginator.get_page(page)

    return render(request, "inventory/supplier_list.html", {
        "suppliers": suppliers_page,
        "search": search,
    })


@login_required
def supplier_detail(request, pk):
    """View supplier details and order history."""
    studio = get_user_studio(request.user)
    from apps.inventory.models import Supplier
    supplier = get_object_or_404(Supplier, pk=pk, studio=studio)
    orders = supplier.orders.select_related("inventory_item").all()[:20]

    return render(request, "inventory/supplier_detail.html", {
        "supplier": supplier,
        "orders": orders,
    })


@login_required
def supplier_create(request):
    """Create a new supplier."""
    studio = get_user_studio(request.user)
    if request.method == "POST":
        from apps.inventory.supplier_service import create_supplier
        data = {
            "name": request.POST.get("name", "").strip(),
            "contact_person": request.POST.get("contact_person", "").strip(),
            "phone": request.POST.get("phone", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "address": request.POST.get("address", "").strip(),
            "city": request.POST.get("city", "").strip(),
            "website": request.POST.get("website", "").strip(),
            "notes": request.POST.get("notes", "").strip(),
        }
        supplier = create_supplier(studio, data, request.user)
        messages.success(request, f"Supplier '{supplier.name}' created.")
        return redirect("inventory:supplier_detail", pk=supplier.pk)

    return render(request, "inventory/supplier_form.html", {"editing": False})


@login_required
def supplier_edit(request, pk):
    """Edit a supplier."""
    studio = get_user_studio(request.user)
    from apps.inventory.models import Supplier
    supplier = get_object_or_404(Supplier, pk=pk, studio=studio)

    if request.method == "POST":
        from apps.inventory.supplier_service import update_supplier
        data = {
            "name": request.POST.get("name", "").strip(),
            "contact_person": request.POST.get("contact_person", "").strip(),
            "phone": request.POST.get("phone", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "address": request.POST.get("address", "").strip(),
            "city": request.POST.get("city", "").strip(),
            "website": request.POST.get("website", "").strip(),
            "notes": request.POST.get("notes", "").strip(),
        }
        update_supplier(supplier, data, request.user)
        messages.success(request, f"Supplier '{supplier.name}' updated.")
        return redirect("inventory:supplier_detail", pk=pk)

    return render(request, "inventory/supplier_form.html", {"supplier": supplier, "editing": True})


@login_required
def supplier_order_create(request, supplier_pk):
    """Create an order to a supplier."""
    studio = get_user_studio(request.user)
    from apps.inventory.models import Supplier
    from decimal import Decimal
    supplier = get_object_or_404(Supplier, pk=supplier_pk, studio=studio)

    if request.method == "POST":
        from apps.inventory.supplier_service import create_supplier_order
        data = {
            "supplier": supplier,
            "item_name": request.POST.get("item_name", "").strip(),
            "quantity": int(request.POST.get("quantity", 1)),
            "unit_cost": Decimal(request.POST.get("unit_cost", "0")),
            "expected_delivery": request.POST.get("expected_delivery") or None,
            "notes": request.POST.get("notes", "").strip(),
        }
        order = create_supplier_order(studio, data, request.user)
        messages.success(request, f"Order {order.order_number} created.")
        return redirect("inventory:supplier_detail", pk=supplier_pk)

    return render(request, "inventory/supplier_order_form.html", {"supplier": supplier})


@login_required
def supplier_order_receive(request, pk):
    """Mark a supplier order as received."""
    studio = get_user_studio(request.user)
    from apps.inventory.models import SupplierOrder
    order = get_object_or_404(SupplierOrder, pk=pk, studio=studio)

    if request.method == "POST":
        from apps.inventory.supplier_service import receive_order
        receive_order(order, request.user)
        messages.success(request, f"Order {order.order_number} marked as delivered.")

    return redirect("inventory:supplier_detail", pk=order.supplier.pk)
