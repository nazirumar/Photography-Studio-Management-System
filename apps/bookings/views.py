import contextlib
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio
from apps.bookings.models import Booking
from apps.bookings.services import (
    create_booking,
    generate_next_reference,
    record_booking_payment,
    update_booking_status,
)


@login_required
def booking_list(request):
    studio = get_user_studio(request.user)
    queryset = Booking.objects.filter(studio=studio).select_related("client", "package")

    search = request.GET.get("q", "").strip()
    if search:
        queryset = queryset.filter(
            Q(reference__icontains=search)
            | Q(title__icontains=search)
            | Q(client__first_name__icontains=search)
            | Q(client__last_name__icontains=search)
        )

    status = request.GET.get("status", "")
    if status:
        queryset = queryset.filter(status=status)

    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")
    if date_from:
        with contextlib.suppress(ValueError, TypeError):
            queryset = queryset.filter(date__gte=date.fromisoformat(date_from))
    if date_to:
        with contextlib.suppress(ValueError, TypeError):
            queryset = queryset.filter(date__lte=date.fromisoformat(date_to))

    paginator = Paginator(queryset, 20)
    page = request.GET.get("page")
    bookings = paginator.get_page(page)

    return render(request, "bookings/list.html", {
        "bookings": bookings,
        "search": search,
        "status": status,
        "date_from": date_from,
        "date_to": date_to,
        "total_count": queryset.count(),
    })


@login_required
def booking_create(request):
    studio = get_user_studio(request.user)
    from apps.packages.forms import BookingForm
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.copy()
            booking = create_booking(studio=studio, data=data, user=request.user)
            messages.success(request, f"Booking {booking.reference} created.")
            return redirect("bookings:detail", pk=booking.pk)
    else:
        form = BookingForm()
        initial_ref = generate_next_reference(studio)
    return render(request, "bookings/form.html", {
        "form": form,
        "title": "New Booking",
        "initial_ref": initial_ref if request.method == "GET" else None,
    })


@login_required
def booking_detail(request, pk):
    studio = get_user_studio(request.user)
    booking = get_object_or_404(
        Booking.objects.select_related("client", "package", "photographer"),
        pk=pk, studio=studio,
    )
    payments = booking.payments.all()[:10]
    return render(request, "bookings/detail.html", {
        "booking": booking,
        "payments": payments,
    })


@login_required
def booking_status_change(request, pk):
    studio = get_user_studio(request.user)
    booking = get_object_or_404(Booking, pk=pk, studio=studio)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status:
            try:
                update_booking_status(booking, new_status, user=request.user)
                messages.success(request, f"Booking status updated to {new_status}.")
            except ValueError as e:
                messages.error(request, str(e))
    return redirect("bookings:detail", pk=pk)


@login_required
def booking_payment(request, pk):
    studio = get_user_studio(request.user)
    booking = get_object_or_404(Booking, pk=pk, studio=studio)
    if request.method == "POST":
        amount = request.POST.get("amount")
        method = request.POST.get("method", "cash")
        reference = request.POST.get("reference", "")
        if amount:
            from decimal import Decimal
            record_booking_payment(
                booking=booking,
                amount=Decimal(amount),
                method=method,
                reference=reference,
                user=request.user,
            )
            messages.success(request, f"Payment of N{amount} recorded.")
    return redirect("bookings:detail", pk=pk)


KANBAN_COLUMNS = [
    Booking.Status.ENQUIRY,
    Booking.Status.TENTATIVE,
    Booking.Status.AWAITING_DEPOSIT,
    Booking.Status.CONFIRMED,
    Booking.Status.IN_PROGRESS,
    Booking.Status.COMPLETED,
]

KANBAN_LABELS = {s: s.replace("_", " ").title() for s in KANBAN_COLUMNS}


@login_required
def booking_kanban(request):
    studio = get_user_studio(request.user)
    bookings = Booking.objects.filter(studio=studio).select_related("client", "package", "photographer")

    columns = {}
    for col in KANBAN_COLUMNS:
        columns[col] = list(bookings.filter(status=col).order_by("-created_at"))

    return render(request, "bookings/kanban.html", {
        "columns": columns,
        "labels": KANBAN_LABELS,
        "all_statuses": [s[0] for s in Booking.Status.choices],
        "all_labels": {s[0]: s[1] for s in Booking.Status.choices},
    })


@login_required
def booking_kanban_move(request, pk):
    """HTMX endpoint for drag-and-drop status updates."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    studio = get_user_studio(request.user)
    booking = get_object_or_404(Booking, pk=pk, studio=studio)

    new_status = request.POST.get("status", "").strip()
    valid_statuses = [s[0] for s in Booking.Status.choices]
    if new_status not in valid_statuses:
        return JsonResponse({"error": "Invalid status"}, status=400)

    try:
        update_booking_status(booking, new_status, user=request.user)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

    if request.headers.get("HX-Request"):
        booking = Booking.objects.select_related("client", "package", "photographer").get(pk=booking.pk)
        return render(request, "bookings/kanban_card.html", {"booking": booking})

    return JsonResponse({"ok": True, "status": new_status})


@login_required
def booking_ical_export(request):
    """Export all bookings as iCal file."""
    from django.http import HttpResponse
    from apps.bookings.calendar_service import generate_studio_calendar
    studio = get_user_studio(request.user)
    bookings = Booking.objects.filter(studio=studio, status__in=["confirmed", "in_progress"])
    ical_data = generate_studio_calendar(bookings)
    response = HttpResponse(ical_data, content_type="text/calendar; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="studioflow-bookings.ics"'
    return response


@login_required
def booking_ical_single(request, pk):
    """Export a single booking as iCal file."""
    from django.http import HttpResponse
    from apps.bookings.calendar_service import generate_booking_ical
    studio = get_user_studio(request.user)
    booking = get_object_or_404(Booking, pk=pk, studio=studio)
    ical_data = generate_booking_ical(booking)
    response = HttpResponse(ical_data, content_type="text/calendar; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{booking.reference}.ics"'
    return response
