from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio
from apps.clients.models import Client

from .communication_models import Communication


@login_required
def communication_list(request, client_pk):
    studio = get_user_studio(request.user)
    client = get_object_or_404(Client, pk=client_pk, studio=studio)
    communications = Communication.objects.filter(client=client).select_related("created_by")
    return render(request, "clients/communications.html", {
        "client": client,
        "communications": communications,
    })


@login_required
def communication_create(request, client_pk):
    studio = get_user_studio(request.user)
    client = get_object_or_404(Client, pk=client_pk, studio=studio)
    if request.method == "POST":
        Communication.objects.create(
            studio=studio,
            client=client,
            communication_type=request.POST.get("communication_type", "note"),
            subject=request.POST.get("subject", ""),
            notes=request.POST.get("notes", ""),
            outcome=request.POST.get("outcome", ""),
            follow_up_date=request.POST.get("follow_up_date") or None,
            created_by=request.user,
        )
        messages.success(request, "Communication logged.")
        return redirect("client_comm:list", client_pk=client.pk)
    return render(request, "clients/communication_form.html", {"client": client})
