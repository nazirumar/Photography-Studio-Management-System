from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio
from apps.equipment.forms import EquipmentForm, EquipmentSearchForm
from apps.equipment.models import Equipment, MaintenanceLog
from apps.equipment.services import (
    assign_equipment,
    create_equipment,
    create_maintenance_log,
    get_maintenance_due,
    get_overdue_maintenance,
    update_equipment,
    update_equipment_status,
)


@login_required
def equipment_list(request):
    studio = get_user_studio(request.user)
    form = EquipmentSearchForm(request.GET or None)
    queryset = Equipment.objects.filter(studio=studio).select_related("assigned_to")

    if form.is_valid():
        q = form.cleaned_data.get("q")
        status = form.cleaned_data.get("status")
        if q:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=q)
                | Q(asset_number__icontains=q)
                | Q(brand__icontains=q)
                | Q(serial_number__icontains=q)
            )
        if status:
            queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, 20)
    page = request.GET.get("page")
    equipment = paginator.get_page(page)

    return render(request, "equipment/list.html", {
        "equipment": equipment,
        "form": form,
        "total_count": queryset.count(),
    })


@login_required
def equipment_create(request):
    studio = get_user_studio(request.user)
    if request.method == "POST":
        form = EquipmentForm(request.POST)
        if form.is_valid():
            create_equipment(studio=studio, data=form.cleaned_data, user=request.user)
            messages.success(request, "Equipment created.")
            return redirect("equipment:list")
    else:
        form = EquipmentForm()
    return render(request, "equipment/form.html", {"form": form, "title": "Add Equipment"})


@login_required
def equipment_detail(request, pk):
    studio = get_user_studio(request.user)
    equipment = get_object_or_404(
        Equipment.objects.select_related("assigned_to"), pk=pk, studio=studio
    )
    return render(request, "equipment/detail.html", {"equipment": equipment, "status_choices": Equipment.Status.choices})


@login_required
def equipment_edit(request, pk):
    studio = get_user_studio(request.user)
    equipment = get_object_or_404(Equipment, pk=pk, studio=studio)
    if request.method == "POST":
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            update_equipment(equipment, form.cleaned_data, user=request.user)
            messages.success(request, "Equipment updated.")
            return redirect("equipment:detail", pk=equipment.pk)
    else:
        form = EquipmentForm(instance=equipment)
    return render(request, "equipment/form.html", {"form": form, "title": "Edit Equipment", "equipment": equipment})


@login_required
def equipment_status_change(request, pk):
    studio = get_user_studio(request.user)
    equipment = get_object_or_404(Equipment, pk=pk, studio=studio)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status:
            update_equipment_status(equipment, new_status, user=request.user)
            messages.success(request, f"Status updated to {new_status}.")
    return redirect("equipment:detail", pk=pk)


@login_required
def equipment_assign(request, pk):
    studio = get_user_studio(request.user)
    equipment = get_object_or_404(Equipment, pk=pk, studio=studio)
    if request.method == "POST":
        assignee_id = request.POST.get("assigned_to")
        from django.contrib.auth import get_user_model
        user_model = get_user_model()
        assignee = user_model.objects.filter(pk=assignee_id).first() if assignee_id else None
        assign_equipment(equipment, assignee, user=request.user)
        messages.success(request, f"Equipment {'assigned' if assignee else 'unassigned'}.")
    return redirect("equipment:detail", pk=pk)


@login_required
def maintenance_due_list(request):
    studio = get_user_studio(request.user)
    items = get_maintenance_due(studio)
    overdue = get_overdue_maintenance(studio)
    return render(request, "equipment/maintenance_due.html", {"items": items, "overdue": overdue})


@login_required
def maintenance_log_add(request, equipment_pk):
    studio = get_user_studio(request.user)
    equipment = get_object_or_404(Equipment, pk=equipment_pk, studio=studio)
    if request.method == "POST":
        from django.utils import timezone
        data = {
            "maintenance_type": request.POST.get("maintenance_type", "scheduled"),
            "description": request.POST.get("description", ""),
            "vendor": request.POST.get("vendor", ""),
            "cost": request.POST.get("cost", 0),
            "performed_date": request.POST.get("performed_date", timezone.now().date()),
            "next_due_date": request.POST.get("next_due_date") or None,
            "notes": request.POST.get("notes", ""),
        }
        create_maintenance_log(equipment, data, user=request.user)
        messages.success(request, "Maintenance log recorded.")
        return redirect("equipment:detail", pk=equipment.pk)
    return render(request, "equipment/maintenance_form.html", {"equipment": equipment})


@login_required
def maintenance_log_list(request, equipment_pk):
    studio = get_user_studio(request.user)
    equipment = get_object_or_404(Equipment, pk=equipment_pk, studio=studio)
    logs = equipment.maintenance_logs.all()
    return render(request, "equipment/maintenance_logs.html", {"equipment": equipment, "logs": logs})
