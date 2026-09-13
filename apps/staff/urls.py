from django.urls import path
from . import views

app_name = "staff"

urlpatterns = [
    path("schedule/", views.staff_schedule_view, name="schedule"),
    path("available/", views.staff_available_api, name="available_api"),
    path("assign/<uuid:booking_pk>/", views.staff_booking_assign, name="assign"),
]
