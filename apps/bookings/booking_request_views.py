from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.services import get_user_studio
from apps.bookings.models import BookingRequest


def booking_request_form(request):
    """Public booking request form - no auth required."""
    from apps.packages.models import Package
    studio_slug = request.resolver_match.kwargs.get("studio_slug")
    # Get default studio (first active)
    from apps.studios.models import Studio
    studio = Studio.objects.first()
    if not studio:
        messages.error(request, "No studio configured.")
        return render(request, "bookings/request_form.html", {"packages": [], "studio": None})

    packages = Package.objects.filter(studio=studio, is_active=True).order_by("name")

    if request.method == "POST":
        from apps.bookings.booking_request_service import create_booking_request
        data = {
            "first_name": request.POST.get("first_name", "").strip(),
            "last_name": request.POST.get("last_name", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "phone": request.POST.get("phone", "").strip(),
            "whatsapp": request.POST.get("whatsapp", "").strip(),
            "event_type": request.POST.get("event_type", "").strip(),
            "preferred_date": request.POST.get("preferred_date"),
            "alternate_date": request.POST.get("alternate_date") or None,
            "package_id": request.POST.get("package") or None,
            "guest_count": request.POST.get("guest_count") or None,
            "location_preference": request.POST.get("location_preference", "no_preference"),
            "budget": request.POST.get("budget") or None,
            "notes": request.POST.get("notes", "").strip(),
        }
        # Validate required fields
        required = ["first_name", "last_name", "email", "event_type", "preferred_date"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            messages.error(request, f"Please fill in: {', '.join(missing)}")
        else:
            try:
                from decimal import Decimal
                if data["budget"]:
                    data["budget"] = Decimal(data["budget"])
                if data["guest_count"]:
                    data["guest_count"] = int(data["guest_count"])
                if data["package_id"]:
                    from apps.packages.models import Package
                    data["package"] = Package.objects.get(pk=data["package_id"], studio=studio)
                else:
                    del data["package_id"]
                # Convert date strings
                from datetime import date as date_type
                data["preferred_date"] = date_type.fromisoformat(data["preferred_date"])
                if data["alternate_date"]:
                    data["alternate_date"] = date_type.fromisoformat(data["alternate_date"])
                else:
                    del data["alternate_date"]
                create_booking_request(studio=studio, data=data)
                return render(request, "bookings/request_success.html", {"studio": studio})
            except Exception as e:
                messages.error(request, f"Error submitting request: {e}")

    return render(request, "bookings/request_form.html", {"packages": packages, "studio": studio})


@login_required
def booking_request_list(request):
    """Staff view of all booking requests."""
    studio = get_user_studio(request.user)
    queryset = BookingRequest.objects.filter(studio=studio)

    status = request.GET.get("status", "")
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, 20)
    page = request.GET.get("page")
    requests_page = paginator.get_page(page)

    return render(request, "bookings/request_list.html", {
        "requests": requests_page,
        "status": status,
        "status_choices": BookingRequest.Status.choices,
        "total_count": queryset.count(),
    })


@login_required
def booking_request_detail(request, pk):
    """Staff view of a single booking request."""
    studio = get_user_studio(request.user)
    booking_request = get_object_or_404(BookingRequest, pk=pk, studio=studio)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "approve":
            from apps.bookings.booking_request_service import review_booking_request
            review_booking_request(booking_request, request.user, approved=True)
            messages.success(request, "Booking request approved.")
        elif action == "decline":
            from apps.bookings.booking_request_service import review_booking_request
            review_booking_request(booking_request, request.user, approved=False)
            messages.success(request, "Booking request declined.")
        elif action == "convert":
            from apps.bookings.booking_request_service import convert_request_to_booking
            booking = convert_request_to_booking(booking_request, request.user)
            messages.success(request, f"Booking {booking.reference} created from request.")
            return redirect("bookings:detail", pk=booking.pk)
        return redirect("bookings:request_detail", pk=pk)

    return render(request, "bookings/request_detail.html", {"booking_request": booking_request})
