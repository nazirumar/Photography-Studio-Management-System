from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class Booking(BaseModel):
    class Status(models.TextChoices):
        ENQUIRY = "enquiry", "Enquiry"
        TENTATIVE = "tentative", "Tentative"
        AWAITING_DEPOSIT = "awaiting_deposit", "Awaiting Deposit"
        CONFIRMED = "confirmed", "Confirmed"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PARTIAL = "partial", "Partially Paid"
        PAID = "paid", "Paid"

    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="bookings")
    reference = models.CharField(max_length=50)
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="bookings")
    package = models.ForeignKey(
        "packages.Package", on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings"
    )
    service = models.ForeignKey("packages.ServiceCategory", on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=300, blank=True)
    event_type = models.CharField(max_length=100, blank=True)
    date = models.DateField(db_index=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=300, blank=True)
    location_type = models.CharField(
        max_length=20,
        choices=[("studio", "Studio"), ("outdoor", "Outdoor"), ("event", "Event")],
        default="studio",
    )
    photographer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="photographer_bookings",
    )
    additional_staff = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="additional_bookings")
    package_snapshot = models.JSONField(default=dict, blank=True)
    base_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    deposit_required = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ENQUIRY, db_index=True)
    special_instructions = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)
    client_notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_bookings"
    )

    class Meta:
        ordering = ["-date", "-start_time"]
        unique_together = [("studio", "reference")]

    def __str__(self):
        return f"{self.reference} - {self.client}"

    def save(self, *args, **kwargs):
        self.balance = self.total_amount - self.amount_paid
        super().save(*args, **kwargs)


class BookingRequest(BaseModel):
    """Public booking request submitted by clients via the website."""
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        REVIEWED = "reviewed", "Reviewed"
        CONVERTED = "converted", "Converted to Booking"
        DECLINED = "declined", "Declined"

    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="booking_requests")
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    event_type = models.CharField(max_length=100)
    preferred_date = models.DateField()
    alternate_date = models.DateField(null=True, blank=True)
    package = models.ForeignKey(
        "packages.Package", on_delete=models.SET_NULL, null=True, blank=True, related_name="requests"
    )
    guest_count = models.PositiveIntegerField(null=True, blank=True)
    location_preference = models.CharField(
        max_length=20,
        choices=[("studio", "Studio"), ("outdoor", "Outdoor"), ("event", "Event"), ("no_preference", "No Preference")],
        default="no_preference",
    )
    budget = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    converted_booking = models.ForeignKey(
        "bookings.Booking", on_delete=models.SET_NULL, null=True, blank=True, related_name="converted_from_requests"
    )
    reviewed_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_requests"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Request: {self.first_name} {self.last_name} - {self.event_type} ({self.preferred_date})"
