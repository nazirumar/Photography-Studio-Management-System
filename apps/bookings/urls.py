from django.urls import include, path

from . import views

app_name = "bookings"

urlpatterns = [
    path("", views.booking_list, name="list"),
    path("kanban/", views.booking_kanban, name="kanban"),
    path("<uuid:pk>/kanban-move/", views.booking_kanban_move, name="kanban_move"),
    path("add/", views.booking_create, name="create"),
    path("<uuid:pk>/", views.booking_detail, name="detail"),
    path("<uuid:pk>/status/", views.booking_status_change, name="status"),
    path("<uuid:pk>/payment/", views.booking_payment, name="payment"),
    path("conflicts/", include("apps.bookings.conflict_urls")),
]
