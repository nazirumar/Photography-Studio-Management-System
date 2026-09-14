from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("", include("apps.dashboard.urls")),
    path("clients/", include("apps.clients.urls")),
    path("leads/", include("apps.leads.urls")),
    path("packages/", include("apps.packages.urls")),
    path("bookings/", include("apps.bookings.urls")),
    path("projects/", include("apps.projects.urls")),
    path("gallery/", include("apps.gallery.upload_urls")),
    path("gallery/", include("apps.gallery.urls")),
    path("finance/", include("apps.finance.urls")),
    path("expenses/", include("apps.expenses.urls")),
    path("inventory/", include("apps.inventory.urls")),
    path("equipment/", include("apps.equipment.urls")),
    path("printing/", include("apps.printing.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("reports/", include("apps.reports.urls")),
    path("audit/", include("apps.audit.urls")),
    path("api/", include("rest_framework.urls")),
    path("api/v1/", include("apps.api.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("portal/", include("apps.portal.urls")),
    path("payments/", include("apps.payments.urls")),
    path("calendar/", include("apps.bookings.calendar_urls")),
    path("export/", include("apps.core.export_urls")),
    path("sms/", include("apps.notifications.sms_urls")),
    path("communications/", include("apps.clients.communication_urls")),
    path("finance/", include("apps.finance.pdf_urls")),
    path("backups/", include("apps.core.backup_urls")),
    path("search/", include("apps.core.search_urls")),
    path("health/", include("apps.core.health_urls")),
    path("ai-fde/", include("apps.ai_fde.urls")),
    path("staff/", include("apps.staff.urls")),
    path("contracts/", include("apps.contracts.urls")),
    path("feedback/", include("apps.feedback.urls")),
    path("debug/login-test/", include("apps.core.debug_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    try:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
