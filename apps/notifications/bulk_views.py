from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.accounts.services import get_user_studio


@login_required
def bulk_message(request):
    """Send bulk SMS/WhatsApp to client segments."""
    studio = get_user_studio(request.user)

    # Get client segments
    from apps.clients.models import Client
    from django.db.models import Count, Q

    clients = Client.objects.filter(studio=studio, status="active")

    # Filter options
    segment = request.GET.get("segment", "")
    if segment == "recent":
        from datetime import timedelta
        from django.utils import timezone
        cutoff = timezone.now() - timedelta(days=90)
        clients = clients.filter(bookings__created_at__gte=cutoff).distinct()
    elif segment == "high_value":
        clients = clients.filter(invoices__total__gte=100000).distinct()
    elif segment == "no_booking":
        clients = clients.filter(bookings__isnull=True)

    if request.method == "POST":
        message_text = request.POST.get("message", "").strip()
        channel = request.POST.get("channel", "sms")
        selected_ids = request.POST.getlist("client_ids")

        if not message_text:
            messages.error(request, "Message is required.")
            return redirect("notifications:bulk_message")

        if not selected_ids:
            messages.error(request, "Select at least one client.")
            return redirect("notifications:bulk_message")

        selected_clients = Client.objects.filter(pk__in=selected_ids, studio=studio)
        sent_count = 0
        failed_count = 0

        sms = None
        if channel in ("sms", "both"):
            from apps.notifications.sms_service import SMSService
            sms = SMSService()

        for client in selected_clients:
            try:
                if channel == "sms" and sms:
                    personalized = message_text.replace("{name}", client.first_name)
                    result = sms.send_sms(client.phone, personalized)
                    sent_count += 1 if result.get("status") else 0
                    failed_count += 0 if result.get("status") else 1
                elif channel == "email":
                    from django.core.mail import send_mail
                    personalized = message_text.replace("{name}", client.first_name)
                    send_mail("Message from Studio", personalized, None, [client.email])
                    sent_count += 1
                elif channel == "whatsapp":
                    from apps.notifications.whatsapp_service import send_whatsapp_message
                    personalized = message_text.replace("{name}", client.first_name)
                    send_whatsapp_message(client.phone, personalized)
                    sent_count += 1
            except Exception:
                failed_count += 1

        messages.success(request, f"Sent: {sent_count}, Failed: {failed_count}")
        return redirect("notifications:bulk_message")

    return render(request, "notifications/bulk_message.html", {
        "clients": clients[:100],
        "segment": segment,
    })
