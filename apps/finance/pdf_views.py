from io import BytesIO

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from apps.accounts.services import get_user_studio
from apps.finance.models import Invoice


@login_required
def invoice_pdf(request, pk):
    studio = get_user_studio(request.user)
    invoice = get_object_or_404(
        Invoice.objects.select_related("client", "booking"),
        pk=pk, studio=studio,
    )
    try:
        from weasyprint import HTML
        html_string = render_to_string("finance/pdf_templates/invoice_pdf.html", {
            "invoice": invoice,
            "studio": studio,
            "payment_url": f"{request.scheme}://{request.get_host()}/payments/pay/{invoice.invoice_number}/",
        })
        pdf_bytes = HTML(string=html_string).write_pdf()
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{invoice.invoice_number}.pdf"'
        return response
    except ImportError:
        html_string = render_to_string("finance/pdf_templates/invoice_pdf.html", {
            "invoice": invoice,
            "studio": studio,
            "payment_url": "",
        })
        return HttpResponse(html_string, content_type="text/html")


@login_required
def quote_pdf(request, pk):
    from apps.bookings.models import Booking
    studio = get_user_studio(request.user)
    booking = get_object_or_404(
        Booking.objects.select_related("client", "package"),
        pk=pk, studio=studio,
    )
    try:
        from weasyprint import HTML
        html_string = render_to_string("finance/pdf_templates/quote_pdf.html", {
            "booking": booking,
            "client": booking.client,
            "studio": studio,
        })
        pdf_bytes = HTML(string=html_string).write_pdf()
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="Quote_{booking.reference}.pdf"'
        return response
    except ImportError:
        html_string = render_to_string("finance/pdf_templates/quote_pdf.html", {
            "booking": booking,
            "client": booking.client,
            "studio": studio,
        })
        return HttpResponse(html_string, content_type="text/html")
