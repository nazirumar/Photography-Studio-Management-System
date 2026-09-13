from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render

from apps.bookings.models import Booking
from apps.clients.models import Client
from apps.finance.models import Invoice, Payment
from apps.gallery.models import Gallery, Photo


def portal_login(request):
    """Client portal login page - redirects to auth view."""
    return redirect("portal:login")


@login_required
def portal_dashboard(request):
    """Client portal dashboard."""
    try:
        client = Client.objects.get(email=request.user.email)
    except Client.DoesNotExist:
        return render(request, "portal/no_access.html")

    bookings = Booking.objects.filter(client=client).select_related("package").order_by("-date")[:5]
    invoices = Invoice.objects.filter(client=client).order_by("-issue_date")[:5]
    galleries = Gallery.objects.filter(
        project__client=client
    ).select_related("project").order_by("-created_at")[:5]

    total_paid = Payment.objects.filter(client=client).aggregate(
        total=models.Sum("amount")
    )["total"] or 0
    total_outstanding = Invoice.objects.filter(client=client).exclude(
        status="paid"
    ).aggregate(total=models.Sum("balance"))["total"] or 0

    return render(request, "portal/dashboard.html", {
        "client": client,
        "bookings": bookings,
        "invoices": invoices,
        "galleries": galleries,
        "total_paid": total_paid,
        "total_outstanding": total_outstanding,
    })


@login_required
def portal_bookings(request):
    """Client portal - view all bookings."""
    try:
        client = Client.objects.get(email=request.user.email)
    except Client.DoesNotExist:
        return render(request, "portal/no_access.html")

    bookings = Booking.objects.filter(client=client).select_related("package").order_by("-date")
    return render(request, "portal/bookings.html", {"client": client, "bookings": bookings})


@login_required
def portal_booking_detail(request, pk):
    """Client portal - view booking status tracker."""
    try:
        client = Client.objects.get(email=request.user.email)
    except Client.DoesNotExist:
        return render(request, "portal/no_access.html")

    booking = get_object_or_404(Booking.objects.select_related("package"), pk=pk, client=client)
    from apps.projects.models import Project
    project = Project.objects.filter(booking=booking).first()
    return render(request, "portal/booking_detail.html", {
        "client": client, "booking": booking, "project": project,
    })


@login_required
def portal_invoices(request):
    """Client portal - view all invoices."""
    try:
        client = Client.objects.get(email=request.user.email)
    except Client.DoesNotExist:
        return render(request, "portal/no_access.html")

    invoices = Invoice.objects.filter(client=client).select_related("booking").order_by("-issue_date")
    return render(request, "portal/invoices.html", {"client": client, "invoices": invoices})


@login_required
def portal_invoice_detail(request, pk):
    """Client portal - view invoice detail."""
    try:
        client = Client.objects.get(email=request.user.email)
    except Client.DoesNotExist:
        return render(request, "portal/no_access.html")

    invoice = get_object_or_404(Invoice, pk=pk, client=client)
    payments = invoice.payments.all().order_by("-payment_date")
    return render(request, "portal/invoice_detail.html", {
        "client": client, "invoice": invoice, "payments": payments,
    })


@login_required
def portal_payment_history(request):
    """Client portal - view payment history."""
    try:
        client = Client.objects.get(email=request.user.email)
    except Client.DoesNotExist:
        return render(request, "portal/no_access.html")

    payments = Payment.objects.filter(client=client).select_related(
        "invoice", "invoice__booking"
    ).order_by("-payment_date")
    return render(request, "portal/payment_history.html", {
        "client": client, "payments": payments,
    })


@login_required
def portal_galleries(request):
    """Client portal - view all galleries."""
    try:
        client = Client.objects.get(email=request.user.email)
    except Client.DoesNotExist:
        return render(request, "portal/no_access.html")

    galleries = Gallery.objects.filter(
        project__client=client
    ).select_related("project").order_by("-created_at")
    return render(request, "portal/galleries.html", {"client": client, "galleries": galleries})


@login_required
def portal_gallery_detail(request, pk):
    """Client portal - view gallery and select photos."""
    try:
        client = Client.objects.get(email=request.user.email)
    except Client.DoesNotExist:
        return render(request, "portal/no_access.html")

    gallery = get_object_or_404(Gallery, pk=pk, project__client=client)
    photos = gallery.photos.all().order_by("image_number")
    selected_count = photos.filter(is_selected=True).count()

    return render(request, "portal/gallery_detail.html", {
        "client": client, "gallery": gallery, "photos": photos,
        "selected_count": selected_count,
    })


@login_required
def portal_photo_select(request, pk):
    """Client portal - toggle photo selection."""
    try:
        client = Client.objects.get(email=request.user.email)
    except Client.DoesNotExist:
        return redirect("portal:dashboard")

    photo = get_object_or_404(Photo, pk=pk, gallery__project__client=client)
    from apps.gallery.services import toggle_photo_selection
    toggle_photo_selection(photo, client, selected=not photo.is_selected)
    return redirect("portal:gallery_detail", pk=photo.gallery.pk)
