from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q

from apps.accounts.services import get_user_studio
from apps.clients.models import Client
from apps.bookings.models import Booking
from apps.finance.models import Invoice
from apps.leads.models import Lead


@login_required
def global_search(request):
    """Global search API endpoint."""
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"results": []})

    studio = get_user_studio(request.user)
    results = []

    # Search clients
    clients = Client.objects.filter(
        studio=studio,
    ).filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query) |
        Q(phone__icontains=query)
    )[:5]

    for client in clients:
        results.append({
            "type": "client",
            "title": client.display_name,
            "subtitle": client.email,
            "url": f"/clients/{client.pk}/",
        })

    # Search bookings
    bookings = Booking.objects.filter(
        studio=studio,
    ).filter(
        Q(reference__icontains=query) |
        Q(title__icontains=query) |
        Q(client__first_name__icontains=query) |
        Q(client__last_name__icontains=query)
    )[:5]

    for booking in bookings:
        results.append({
            "type": "booking",
            "title": booking.title or booking.reference,
            "subtitle": f"{booking.client.display_name} - {booking.date}",
            "url": f"/bookings/{booking.pk}/",
        })

    # Search invoices
    invoices = Invoice.objects.filter(
        booking__studio=studio,
    ).filter(
        Q(invoice_number__icontains=query) |
        Q(client__first_name__icontains=query) |
        Q(client__last_name__icontains=query)
    )[:5]

    for invoice in invoices:
        results.append({
            "type": "invoice",
            "title": invoice.invoice_number,
            "subtitle": f"{invoice.client.display_name} - N{invoice.total:,.2f}",
            "url": f"/finance/{invoice.pk}/",
        })

    # Search leads
    leads = Lead.objects.filter(
        studio=studio,
    ).filter(
        Q(name__icontains=query) |
        Q(email__icontains=query) |
        Q(phone__icontains=query)
    )[:5]

    for lead in leads:
        results.append({
            "type": "lead",
            "title": lead.name,
            "subtitle": lead.email or lead.phone,
            "url": f"/leads/{lead.pk}/",
        })

    return JsonResponse({"results": results[:15]})
