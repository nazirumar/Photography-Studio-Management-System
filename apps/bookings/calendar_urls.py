from django.urls import path

from . import calendar_views

app_name = "bookings_calendar"

urlpatterns = [
    path("", calendar_views.booking_calendar, name="calendar"),
]
