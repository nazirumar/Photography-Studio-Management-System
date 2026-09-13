import json
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.accounts.services import get_user_studio


@login_required
def invoice_pay_online(request, pk):
    """Generate Paystack payment link for an invoice."""
    studio = get_user_studio(request.user)
    from apps.finance.models import Invoice
    invoice = get_object_or_404(Invoice, pk=pk, studio=studio)

    from apps.finance.payment_service import create_payment_link
    result = create_payment_link(invoice)

    if result:
        return redirect(result["authorization_url"])
    else:
        messages.error(request, "Unable to generate payment link. Please check Paystack configuration.")
        return redirect("finance:invoice_detail", pk=pk)


@csrf_exempt
@require_POST
def paystack_webhook(request):
    """Handle Paystack webhook for payment confirmation."""
    from apps.finance.payment_service import PaystackService, handle_paystack_webhook
    from django.http import HttpResponse

    service = PaystackService()

    # Verify webhook signature
    signature = request.headers.get("X-Paystack-Signature", "")
    if not service.verify_webhook(request.body, signature):
        return HttpResponse("Invalid signature", status=400)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse("Invalid JSON", status=400)

    result = handle_paystack_webhook(payload)
    return HttpResponse("OK", status=200)


@login_required
def payment_link_page(request, pk):
    """Client-facing payment page (public-ish, no auth required but validates invoice)."""
    from apps.finance.models import Invoice
    invoice = get_object_or_404(Invoice, pk=pk)

    from apps.finance.payment_service import create_payment_link
    result = create_payment_link(invoice)

    return render(request, "finance/payment_link.html", {
        "invoice": invoice,
        "payment_result": result,
    })
