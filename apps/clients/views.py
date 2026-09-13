from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio
from apps.clients.forms import ClientForm
from apps.clients.models import Client
from apps.clients.services import (
    archive_client,
    create_client,
    generate_next_client_number,
    get_client_balance,
    get_client_lifetime_value,
    update_client,
)


@login_required
def client_list(request):
    studio = get_user_studio(request.user)
    queryset = Client.objects.filter(studio=studio)

    search = request.GET.get("q", "").strip()
    if search:
        queryset = queryset.filter(
            Q(client_number__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
            | Q(phone__icontains=search)
        )

    status = request.GET.get("status", "")
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, 20)
    page = request.GET.get("page")
    clients = paginator.get_page(page)

    return render(request, "clients/list.html", {
        "clients": clients,
        "search": search,
        "status": status,
        "total_count": queryset.count(),
    })


@login_required
def client_create(request):
    studio = get_user_studio(request.user)
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.copy()
            data["client_number"] = generate_next_client_number(studio)
            client = create_client(studio=studio, data=data, user=request.user)
            messages.success(request, f"Client {client.display_name} created.")
            return redirect("clients:detail", pk=client.pk)
    else:
        form = ClientForm()
    return render(request, "clients/form.html", {"form": form, "title": "Add Client"})


@login_required
def client_detail(request, pk):
    studio = get_user_studio(request.user)
    client = get_object_or_404(
        Client.objects.prefetch_related("bookings", "projects", "invoices", "payments"),
        pk=pk, studio=studio,
    )
    balance = get_client_balance(client)
    lifetime_value = get_client_lifetime_value(client)
    bookings = client.bookings.all()[:10]
    projects = client.projects.all()[:10]
    invoices = client.invoices.all()[:10]
    payments = client.payments.all()[:10]

    return render(request, "clients/detail.html", {
        "client": client,
        "balance": balance,
        "lifetime_value": lifetime_value,
        "bookings": bookings,
        "projects": projects,
        "invoices": invoices,
        "payments": payments,
    })


@login_required
def client_edit(request, pk):
    studio = get_user_studio(request.user)
    client = get_object_or_404(Client, pk=pk, studio=studio)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            client = update_client(client, form.cleaned_data, user=request.user)
            messages.success(request, f"Client {client.display_name} updated.")
            return redirect("clients:detail", pk=client.pk)
    else:
        form = ClientForm(instance=client)
    return render(request, "clients/form.html", {"form": form, "title": "Edit Client", "client": client})


@login_required
def client_archive(request, pk):
    studio = get_user_studio(request.user)
    client = get_object_or_404(Client, pk=pk, studio=studio)
    if request.method == "POST":
        archive_client(client, user=request.user)
        messages.success(request, f"Client {client.display_name} archived.")
        return redirect("clients:list")
    return render(request, "clients/archive_confirm.html", {"client": client})
