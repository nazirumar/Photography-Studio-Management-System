from django.urls import path, include

from . import views, sms_views, bulk_views

app_name = "notifications"

urlpatterns = [
    path("", views.notification_list, name="list"),
    path("<uuid:pk>/read/", views.notification_mark_read, name="mark_read"),
    path("mark-all-read/", views.notification_mark_all_read, name="mark_all_read"),
    path("unread-count/", views.notification_unread_count, name="unread_count"),
    path("cleanup/", views.notification_cleanup, name="cleanup"),
    path("email/", include("apps.notifications.email_urls")),
    path("sms-status/", sms_views.sms_dashboard, name="sms_dashboard"),
    path("bulk/", bulk_views.bulk_message, name="bulk_message"),
]
