from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio
from apps.clients.models import Client
from apps.notifications.models import SMSDeliveryLog
from apps.notifications.sms_service import SMSService


@login_required
def send_sms_view(request):
    studio = get_user_studio(request.user)
    sms = SMSService()

    if not sms.is_configured:
        messages.warning(request, "SMS service not configured. Set TERMII_API_KEY in your .env file.")

    if request.method == "POST":
        phone = request.POST.get("phone", "")
        message = request.POST.get("message", "")
        if phone and message:
            result = sms.send_sms(phone, message)
            if result.get("status"):
                messages.success(request, "SMS sent successfully.")
            else:
                error = result.get("error", "Unknown error")
                messages.error(request, f"SMS failed: {error}")
        else:
            messages.error(request, "Please provide a phone number and message.")
        return redirect("sms:send")
    clients = Client.objects.filter(studio=studio, status="active")
    return render(request, "notifications/send_sms.html", {"clients": clients, "sms_configured": sms.is_configured})


@login_required
def send_bulk_sms(request):
    studio = get_user_studio(request.user)
    sms = SMSService()

    if not sms.is_configured:
        messages.warning(request, "SMS service not configured. Set TERMII_API_KEY in your .env file.")

    if request.method == "POST":
        message = request.POST.get("message", "")
        client_ids = request.POST.getlist("client_ids")
        if message and client_ids:
            sent = 0
            failed = 0
            for cid in client_ids:
                try:
                    client = Client.objects.get(pk=cid, studio=studio)
                    if client.phone:
                        result = sms.send_sms(client.phone, message)
                        if result.get("status"):
                            sent += 1
                        else:
                            failed += 1
                except Client.DoesNotExist:
                    continue
            if sent > 0:
                messages.success(request, f"SMS sent to {sent} clients." + (f" {failed} failed." if failed else ""))
            else:
                messages.error(request, "Failed to send SMS. Check your configuration.")
        else:
            messages.error(request, "Please provide a message and select at least one client.")
        return redirect("sms:send")
    clients = Client.objects.filter(studio=studio, status="active")
    return render(request, "notifications/send_sms.html", {"clients": clients, "bulk": True, "sms_configured": sms.is_configured})


@login_required
def sms_dashboard(request):
    """View SMS delivery status dashboard."""
    studio = get_user_studio(request.user)
    queryset = SMSDeliveryLog.objects.filter(studio=studio)

    status_filter = request.GET.get("status", "")
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    paginator = Paginator(queryset, 20)
    page = request.GET.get("page")
    logs = paginator.get_page(page)

    total = SMSDeliveryLog.objects.filter(studio=studio).count()
    delivered = SMSDeliveryLog.objects.filter(studio=studio, status="delivered").count()
    failed = SMSDeliveryLog.objects.filter(studio=studio, status="failed").count()
    pending = SMSDeliveryLog.objects.filter(studio=studio, status__in=["pending", "sent"]).count()

    sms = SMSService()

    return render(request, "notifications/sms_dashboard.html", {
        "logs": logs,
        "status_filter": status_filter,
        "status_choices": SMSDeliveryLog.Status.choices,
        "total": total,
        "delivered": delivered,
        "failed": failed,
        "pending": pending,
        "sms_configured": sms.is_configured,
    })
