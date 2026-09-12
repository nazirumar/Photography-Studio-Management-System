from django.urls import path

from . import views, auth_views

app_name = "portal"

urlpatterns = [
    path("", views.portal_dashboard, name="dashboard"),
    path("login/", auth_views.portal_login_view, name="login"),
    path("logout/", auth_views.portal_logout_view, name="logout"),
    path("profile/", auth_views.portal_profile, name="profile"),
    path("bookings/", views.portal_bookings, name="bookings"),
    path("bookings/<uuid:pk>/", views.portal_booking_detail, name="booking_detail"),
    path("invoices/", views.portal_invoices, name="invoices"),
    path("invoices/<uuid:pk>/", views.portal_invoice_detail, name="invoice_detail"),
    path("payments/", views.portal_payment_history, name="payment_history"),
    path("galleries/", views.portal_galleries, name="galleries"),
    path("galleries/<uuid:pk>/", views.portal_gallery_detail, name="gallery_detail"),
    path("photos/<uuid:pk>/select/", views.portal_photo_select, name="photo_select"),
]
