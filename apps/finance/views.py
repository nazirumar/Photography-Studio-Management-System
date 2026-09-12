from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio
from apps.finance.forms import InvoiceForm, InvoiceItemFormSet, PaymentForm
from apps.finance.models import Invoice, Payment
from apps.finance.services import (
    create_invoice,
    create_invoice_from_booking,
    get_revenue_summary,
    record_invoice_payment,
    void_invoice,
)


@login_required
def invoice_list(request):
    studio = get_user_studio(request.user)
    queryset = Invoice.objects.filter(studio=studio).select_related("client")

    search = request.GET.get("q", "").strip()
    if search:
        queryset = queryset.filter(
            Q(invoice_number__icontains=search)
            | Q(client__first_name__icontains=search)
            | Q(client__last_name__icontains=search)
        )

    status = request.GET.get("status", "")
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, 20)
    page = request.GET.get("page")
    invoices = paginator.get_page(page)

    return render(request, "finance/invoice_list.html", {
        "invoices": invoices,
        "search": search,
        "status": status,
        "total_count": queryset.count(),
    })


@login_required
def invoice_detail(request, pk):
    studio = get_user_studio(request.user)
    invoice = get_object_or_404(
        Invoice.objects.select_related("client"), pk=pk, studio=studio
    )
    items = invoice.items.all()
    payments = invoice.payments.all()[:10]
    payment_form = PaymentForm()
    return render(request, "finance/invoice_detail.html", {
        "invoice": invoice,
        "items": items,
        "payments": payments,
        "payment_form": payment_form,
    })


@login_required
def invoice_create(request):
    studio = get_user_studio(request.user)
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        item_formset = InvoiceItemFormSet(request.POST)
        if form.is_valid() and item_formset.is_valid():
            data = form.cleaned_data.copy()
            items = []
            for item_form in item_formset:
                if item_form.cleaned_data and item_form.cleaned_data.get("description"):
                    items.append(item_form.cleaned_data)
            data["items"] = items
            invoice = create_invoice(studio=studio, data=data, user=request.user)
            messages.success(request, f"Invoice {invoice.invoice_number} created.")
            return redirect("finance:invoice_detail", pk=invoice.pk)
    else:
        form = InvoiceForm()
        item_formset = InvoiceItemFormSet()
    return render(request, "finance/invoice_form.html", {
        "form": form,
        "item_formset": item_formset,
        "title": "New Invoice",
    })


@login_required
def invoice_from_booking(request, booking_pk):
    studio = get_user_studio(request.user)
    from apps.bookings.models import Booking
    booking = get_object_or_404(Booking, pk=booking_pk, studio=studio)
    if request.method == "POST":
        invoice = create_invoice_from_booking(booking, user=request.user)
        messages.success(request, f"Invoice {invoice.invoice_number} created from booking.")
        return redirect("finance:invoice_detail", pk=invoice.pk)
    return render(request, "finance/invoice_from_booking.html", {"booking": booking})


@login_required
def invoice_payment(request, pk):
    studio = get_user_studio(request.user)
    invoice = get_object_or_404(Invoice, pk=pk, studio=studio)
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            record_invoice_payment(
                invoice=invoice,
                amount=cd["amount"],
                method=cd["method"],
                reference=cd["reference"],
                user=request.user,
                payment_date=cd["payment_date"],
            )
            messages.success(request, f"Payment of N{cd['amount']} recorded.")
    return redirect("finance:invoice_detail", pk=pk)


@login_required
def invoice_void(request, pk):
    studio = get_user_studio(request.user)
    invoice = get_object_or_404(Invoice, pk=pk, studio=studio)
    if request.method == "POST":
        void_invoice(invoice, user=request.user)
        messages.success(request, f"Invoice {invoice.invoice_number} voided.")
    return redirect("finance:invoice_detail", pk=pk)


@login_required
def revenue_report(request):
    studio = get_user_studio(request.user)
    from datetime import date
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    df = date.fromisoformat(date_from) if date_from else None
    dt = date.fromisoformat(date_to) if date_to else None
    summary = get_revenue_summary(studio, date_from=df, date_to=dt)
    return render(request, "finance/revenue_report.html", {
        "summary": summary,
        "date_from": date_from or "",
        "date_to": date_to or "",
    })


@login_required
def payment_list(request):
    studio = get_user_studio(request.user)
    payments = Payment.objects.filter(studio=studio).select_related("client", "invoice")[:50]
    return render(request, "finance/payment_list.html", {"payments": payments})
