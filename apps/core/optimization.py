"""Query optimization helpers for StudioFlow."""

from django.db.models import Prefetch


def optimize_booking_queries(queryset):
    """Optimize booking queryset with select_related and prefetch_related."""
    from apps.finance.models import Payment

    return queryset.select_related(
        "client", "package", "studio", "project",
        "photographer", "created_by",
    ).prefetch_related(
        Prefetch(
            "payments",
            queryset=Payment.objects.select_related("invoice").order_by("-payment_date"),
        ),
        "invoices", "tasks",
    )


def optimize_invoice_queries(queryset):
    """Optimize invoice queryset."""
    from apps.finance.models import InvoiceItem, Payment

    return queryset.select_related(
        "client", "booking", "project", "studio",
    ).prefetch_related(
        Prefetch(
            "items",
            queryset=InvoiceItem.objects.all(),
        ),
        Prefetch(
            "payments",
            queryset=Payment.objects.order_by("-payment_date"),
        ),
    )


def optimize_client_queries(queryset):
    """Optimize client queryset."""
    from apps.bookings.models import Booking

    return queryset.prefetch_related(
        Prefetch(
            "bookings",
            queryset=Booking.objects.filter(
                status__in=["confirmed", "completed"]
            ).select_related("package").order_by("-date")[:5],
        ),
    )


def optimize_project_queries(queryset):
    """Optimize project queryset."""
    return queryset.select_related(
        "client", "studio", "package",
        "photographer", "editor", "project_manager",
    ).prefetch_related(
        "galleries", "tasks", "print_jobs", "frame_orders", "album_orders",
    )


def optimize_payment_queries(queryset):
    """Optimize payment queryset."""
    return queryset.select_related(
        "client", "invoice", "booking", "studio", "recorded_by",
    )


def optimize_audit_queries(queryset):
    """Optimize audit log queryset."""
    return queryset.select_related("user")
