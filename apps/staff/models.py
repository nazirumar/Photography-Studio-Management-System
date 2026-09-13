from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class StaffSchedule(BaseModel):
    """Weekly availability schedule for staff members."""
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="staff_schedules")
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="schedules")
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ["day_of_week", "start_time"]
        unique_together = [("studio", "staff", "day_of_week", "start_time")]

    def __str__(self):
        return f"{self.staff} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class StaffBooking(BaseModel):
    """Links staff to specific booking assignments with schedule info."""
    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="staff_bookings")
    booking = models.ForeignKey("bookings.Booking", on_delete=models.CASCADE, related_name="staff_assignments")
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="booking_assignments")
    role = models.CharField(max_length=100, blank=True, help_text="Role for this specific booking (e.g. lead photographer)")
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("booking", "staff")]

    def __str__(self):
        return f"{self.staff} assigned to {self.booking.reference}"
