from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio
from apps.leads.forms import LeadForm, LeadSearchForm
from apps.leads.models import Lead
from apps.leads.services import (
    convert_lead_to_client,
    create_lead,
    get_lead_pipeline_counts,
    update_lead,
)


@login_required
def lead_list(request):
    studio = get_user_studio(request.user)
    form = LeadSearchForm(request.GET or None)
    queryset = Lead.objects.filter(studio=studio)

    if form.is_valid():
        q = form.cleaned_data.get("q")
        status = form.cleaned_data.get("status")
        if q:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=q)
                | Q(email__icontains=q)
                | Q(phone__icontains=q)
            )
        if status:
            queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, 20)
    page = request.GET.get("page")
    leads = paginator.get_page(page)

    pipeline = get_lead_pipeline_counts(studio)
    pipeline_dict = {item["status"]: item["count"] for item in pipeline}

    return render(request, "leads/list.html", {
        "leads": leads,
        "form": form,
        "pipeline": pipeline_dict,
        "total_count": queryset.count(),
    })


@login_required
def lead_create(request):
    studio = get_user_studio(request.user)
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = create_lead(studio=studio, data=form.cleaned_data, user=request.user)
            messages.success(request, f"Lead {lead.name} created.")
            return redirect("leads:detail", pk=lead.pk)
    else:
        form = LeadForm()
    return render(request, "leads/form.html", {"form": form, "title": "Add Lead"})


@login_required
def lead_detail(request, pk):
    studio = get_user_studio(request.user)
    lead = get_object_or_404(Lead, pk=pk, studio=studio)
    return render(request, "leads/detail.html", {"lead": lead})


@login_required
def lead_edit(request, pk):
    studio = get_user_studio(request.user)
    lead = get_object_or_404(Lead, pk=pk, studio=studio)
    if request.method == "POST":
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            lead = update_lead(lead, form.cleaned_data, user=request.user)
            messages.success(request, f"Lead {lead.name} updated.")
            return redirect("leads:detail", pk=lead.pk)
    else:
        form = LeadForm(instance=lead)
    return render(request, "leads/form.html", {"form": form, "title": "Edit Lead", "lead": lead})


@login_required
def lead_convert(request, pk):
    studio = get_user_studio(request.user)
    lead = get_object_or_404(Lead, pk=pk, studio=studio)
    if request.method == "POST":
        client = convert_lead_to_client(lead, user=request.user)
        messages.success(request, f"Lead converted to client {client.client_number}.")
        return redirect("clients:detail", pk=client.pk)
    return render(request, "leads/convert_confirm.html", {"lead": lead})
