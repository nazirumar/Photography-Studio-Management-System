from decimal import Decimal
import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.accounts.services import get_user_studio
from apps.finance.services import record_invoice_payment

from .models import PaymentLink, WebhookLog
from .paystack import PaystackService

logger = logging.getLogger("payments")


@login_required
def payment_link_list(request):
    studio = get_user_studio(request.user)
    links = PaymentLink.objects.filter(studio=studio).select_related("client", "invoice")
    return render(request, "payments/link_list.html", {"links": links})


@login_required
def payment_link_create(request):
    studio = get_user_studio(request.user)
    if request.method == "POST":
        from apps.clients.models import Client
        client_id = request.POST.get("client_id")
        amount = Decimal(request.POST.get("amount", "0"))
        description = request.POST.get("description", "")
        client = get_object_or_404(Client, pk=client_id, studio=studio)
        link = PaymentLink.objects.create(
            studio=studio,
            client=client,
            amount=amount,
            description=description,
        )
        return redirect("payments:link_detail", pk=link.pk)
    from apps.clients.models import Client
    clients = Client.objects.filter(studio=studio, status="active")
    return render(request, "payments/link_form.html", {"clients": clients})


@login_required
def payment_link_detail(request, pk):
    studio = get_user_studio(request.user)
    link = get_object_or_404(PaymentLink, pk=pk, studio=studio)
    paystack = PaystackService()
    return render(request, "payments/link_detail.html", {
        "link": link,
        "paystack_public_key": paystack.public_key,
    })


def payment_link_public(request, reference):
    """Public page for client to make payment."""
    link = get_object_or_404(PaymentLink, reference=reference, is_active=True, paid=False)
    paystack = PaystackService()
    if request.method == "POST":
        email = request.POST.get("email", link.client.email)
        callback_url = request.build_absolute_uri(f"/payments/verify/{link.reference}/")
        result = paystack.initialize_transaction(
            email=email,
            amount=link.amount,
            reference=link.reference,
            callback_url=callback_url,
            metadata={"payment_link_id": str(link.pk)},
        )
        if result.get("status"):
            return redirect(result["data"]["authorization_url"])
        error_msg = result.get("message", "Payment initialization failed. Please try again.")
        logger.warning(f"Paystack init failed for {reference}: {error_msg}")
        return render(request, "payments/public_pay.html", {
            "link": link, "error": error_msg, "paystack_public_key": paystack.public_key,
        })
    return render(request, "payments/public_pay.html", {"link": link, "paystack_public_key": paystack.public_key})


def payment_verify(request, reference):
    """Paystack callback - verify payment."""
    link = get_object_or_404(PaymentLink, reference=reference)
    paystack = PaystackService()
    result = paystack.verify_transaction(reference)
    if result.get("status") and result["data"]["status"] == "success":
        link.paid = True
        link.paid_at = timezone.now()
        link.paystack_reference = result["data"]["reference"]
        link.save(update_fields=["paid", "paid_at", "paystack_reference"])
        if link.invoice:
            from apps.accounts.services import get_user_studio
            record_invoice_payment(
                invoice=link.invoice,
                amount=link.amount,
                method="online",
                reference=link.reference,
                user=None,
            )
        return render(request, "payments/success.html", {"link": link})
    return render(request, "payments/failed.html", {"link": link})


@csrf_exempt
@require_POST
def paystack_webhook(request):
    """Handle Paystack webhooks."""
    signature = request.headers.get("X-Paystack-Signature", "")
    payload = request.body.decode("utf-8")
    paystack = PaystackService()

    from django.conf import settings
    if not PaystackService.verify_webhook_signature(signature, payload, settings.PAYSTACK_SECRET_KEY):
        return JsonResponse({"error": "Invalid signature"}, status=400)

    event = json.loads(payload)
    webhook_log = WebhookLog.objects.create(
        event_type=event.get("event", ""),
        payload=event,
    )

    if event.get("event") == "charge.success":
        reference = event["data"]["reference"]
        try:
            link = PaymentLink.objects.get(reference=reference)
            link.paid = True
            link.paid_at = timezone.now()
            link.paystack_reference = event["data"]["reference"]
            link.save(update_fields=["paid", "paid_at", "paystack_reference"])
            if link.invoice:
                record_invoice_payment(
                    invoice=link.invoice,
                    amount=Decimal(str(event["data"]["amount"] / 100)),
                    method="online",
                    reference=reference,
                    user=None,
                )
            webhook_log.processed = True
            webhook_log.save(update_fields=["processed"])
        except PaymentLink.DoesNotExist:
            webhook_log.error_message = f"No payment link found for reference {reference}"
            webhook_log.save(update_fields=["error_message"])

    return JsonResponse({"status": "ok"})
