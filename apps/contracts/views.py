from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio


@login_required
def contract_create(request, booking_pk):
    """Create a contract for a booking."""
    studio = get_user_studio(request.user)
    from apps.bookings.models import Booking
    booking = get_object_or_404(Booking, pk=booking_pk, studio=studio)

    if request.method == "POST":
        from apps.contracts.contract_service import create_contract
        terms = request.POST.get("terms", "")
        contract = create_contract(studio, booking, request.user, terms=terms or None)
        messages.success(request, f"Contract {contract.contract_number} created.")
        return redirect("contracts:detail", pk=contract.pk)

    from apps.contracts.contract_service import _default_terms
    return render(request, "contracts/create.html", {
        "booking": booking,
        "default_terms": _default_terms(booking),
    })


@login_required
def contract_detail(request, pk):
    """View contract details."""
    studio = get_user_studio(request.user)
    from apps.contracts.models import Contract
    contract = get_object_or_404(Contract, pk=pk, studio=studio)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "send":
            from apps.contracts.contract_service import send_contract
            send_contract(contract, request.user)
            messages.success(request, "Contract sent to client.")
        elif action == "sign":
            signature = request.POST.get("signature", "")
            signer = request.POST.get("signer_type", "client")
            from apps.contracts.contract_service import sign_contract
            sign_contract(contract, signature, signer_type=signer)
            messages.success(request, f"Contract signed by {signer}.")
        return redirect("contracts:detail", pk=pk)

    return render(request, "contracts/detail.html", {"contract": contract})


@login_required
def contract_list(request):
    """List all contracts."""
    studio = get_user_studio(request.user)
    from apps.contracts.models import Contract
    from django.core.paginator import Paginator
    from django.db.models import Q

    queryset = Contract.objects.filter(studio=studio).select_related("booking", "booking__client")
    status = request.GET.get("status", "")
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, 20)
    page = request.GET.get("page")
    contracts = paginator.get_page(page)

    return render(request, "contracts/list.html", {
        "contracts": contracts,
        "status": status,
        "status_choices": Contract.Status.choices,
    })


@login_required
def contract_preview(request, pk):
    """Printable contract preview."""
    studio = get_user_studio(request.user)
    from apps.contracts.models import Contract
    contract = get_object_or_404(Contract, pk=pk, studio=studio)
    return render(request, "contracts/preview.html", {"contract": contract})
