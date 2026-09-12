from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect

from apps.accounts.services import get_user_studio
from apps.finance.models import Invoice, Payment
from apps.projects.models import Project
from apps.bookings.models import Booking

from .email_service import (
    send_invoice_email,
    send_payment_receipt,
    send_booking_confirmation,
    send_selection_ready_email,
    send_delivery_email,
    send_custom_email,
)


@login_required
def send_invoice(request, pk):
    """Send invoice email."""
    if request.method != "POST":
        return redirect("finance:invoice_detail", pk=pk)
    studio = get_user_studio(request.user)
    invoice = get_object_or_404(Invoice, pk=pk, booking__studio=studio)
    success = send_invoice_email(invoice)
    if request.headers.get("HX-Request"):
        return JsonResponse({"success": success})
    return redirect("finance:invoice_detail", pk=pk)


@login_required
def send_receipt(request, pk):
    """Send payment receipt email."""
    if request.method != "POST":
        return redirect("finance:payment_list")
    studio = get_user_studio(request.user)
    payment = get_object_or_404(Payment, pk=pk, studio=studio)
    success = send_payment_receipt(payment)
    if request.headers.get("HX-Request"):
        return JsonResponse({"success": success})
    return redirect("finance:payment_list")


@login_required
def send_booking_email(request, pk):
    """Send booking confirmation email."""
    if request.method != "POST":
        return redirect("bookings:detail", pk=pk)
    studio = get_user_studio(request.user)
    booking = get_object_or_404(Booking, pk=pk, studio=studio)
    success = send_booking_confirmation(booking)
    if request.headers.get("HX-Request"):
        return JsonResponse({"success": success})
    return redirect("bookings:detail", pk=pk)


@login_required
def send_selection_email(request, pk):
    """Send selection ready email."""
    if request.method != "POST":
        return redirect("projects:detail", pk=pk)
    studio = get_user_studio(request.user)
    project = get_object_or_404(Project, pk=pk, studio=studio)
    success = send_selection_ready_email(project)
    if request.headers.get("HX-Request"):
        return JsonResponse({"success": success})
    return redirect("projects:detail", pk=pk)


@login_required
def send_delivery_email_view(request, pk):
    """Send delivery notification email."""
    if request.method != "POST":
        return redirect("projects:detail", pk=pk)
    studio = get_user_studio(request.user)
    project = get_object_or_404(Project, pk=pk, studio=studio)
    success = send_delivery_email(project)
    if request.headers.get("HX-Request"):
        return JsonResponse({"success": success})
    return redirect("projects:detail", pk=pk)
