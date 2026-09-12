import csv
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render

from apps.accounts.services import get_user_studio
from apps.clients.models import Client


class Echo:
    """Pseudo-buffer for streaming CSV writes."""
    def write(self, value):
        return value


@login_required
def export_clients_csv(request):
    studio = get_user_studio(request.user)
    clients = Client.objects.filter(studio=studio).select_related("assigned_to").order_by("-created_at")

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = f'attachment; filename="clients_{datetime.now():%Y%m%d}.csv"'
    response.write("\ufeff")  # BOM for Excel

    writer = csv.writer(response)
    writer.writerow([
        "Client Number", "First Name", "Last Name", "Phone", "WhatsApp",
        "Email", "City", "State", "Status", "Referral Source", "Created",
    ])
    for c in clients:
        writer.writerow([
            c.client_number, c.first_name, c.last_name, c.phone, c.whatsapp,
            c.email, c.city, c.state, c.status, c.referral_source,
            c.created_at.strftime("%Y-%m-%d"),
        ])
    return response


@login_required
def export_bookings_csv(request):
    from apps.bookings.models import Booking
    studio = get_user_studio(request.user)
    bookings = Booking.objects.filter(studio=studio).select_related("client", "package").order_by("-date")

    status = request.GET.get("status", "")
    if status:
        bookings = bookings.filter(status=status)

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = f'attachment; filename="bookings_{datetime.now():%Y%m%d}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow([
        "Reference", "Client", "Package", "Date", "Event Type",
        "Location", "Status", "Total Amount", "Amount Paid", "Balance",
    ])
    for b in bookings:
        writer.writerow([
            b.reference, str(b.client), str(b.package) if b.package else "",
            b.date.strftime("%Y-%m-%d") if b.date else "", b.event_type,
            b.location, b.get_status_display(),
            b.total_amount, b.amount_paid, b.balance,
        ])
    return response


@login_required
def export_invoices_csv(request):
    from apps.finance.models import Invoice
    studio = get_user_studio(request.user)
    invoices = Invoice.objects.filter(studio=studio).select_related("client").order_by("-issue_date")

    status = request.GET.get("status", "")
    if status:
        invoices = invoices.filter(status=status)

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = f'attachment; filename="invoices_{datetime.now():%Y%m%d}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow([
        "Invoice Number", "Client", "Issue Date", "Due Date",
        "Subtotal", "Tax", "Total", "Amount Paid", "Balance", "Status",
    ])
    for inv in invoices:
        writer.writerow([
            inv.invoice_number, str(inv.client),
            inv.issue_date.strftime("%Y-%m-%d"),
            inv.due_date.strftime("%Y-%m-%d") if inv.due_date else "",
            inv.subtotal, inv.tax, inv.total, inv.amount_paid,
            inv.balance, inv.get_status_display(),
        ])
    return response


@login_required
def export_expenses_csv(request):
    from apps.expenses.models import Expense
    studio = get_user_studio(request.user)
    expenses = Expense.objects.filter(studio=studio).select_related("category").order_by("-date")

    category = request.GET.get("category", "")
    if category:
        expenses = expenses.filter(category_id=category)

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = f'attachment; filename="expenses_{datetime.now():%Y%m%d}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow([
        "Reference", "Category", "Vendor", "Description",
        "Amount", "Date", "Payment Method",
    ])
    for exp in expenses:
        writer.writerow([
            exp.reference, str(exp.category) if exp.category else "",
            exp.vendor, exp.description, exp.amount,
            exp.date.strftime("%Y-%m-%d"), exp.payment_method,
        ])
    return response


@login_required
def export_clients_import(request):
    studio = get_user_studio(request.user)
    if request.method != "POST":
        return render(request, "core/import.html")

    csv_file = request.FILES.get("file")
    if not csv_file:
        messages.error(request, "Please select a CSV file.")
        return render(request, "core/import.html")

    try:
        decoded = csv_file.read().decode("utf-8-sig")
        reader = csv.DictReader(decoded.splitlines())
        count = 0
        for row in reader:
            first = row.get("first_name", "").strip()
            last = row.get("last_name", "").strip()
            if not first or not last:
                continue
            Client.objects.create(
                studio=studio,
                client_number=f"IMP-{count+1:04d}",
                first_name=first,
                last_name=last,
                phone=row.get("phone", "").strip(),
                email=row.get("email", "").strip(),
                city=row.get("city", "").strip(),
                state=row.get("state", "").strip(),
            )
            count += 1
        messages.success(request, f"Successfully imported {count} clients.")
    except Exception as e:
        messages.error(request, f"Import failed: {e}")

    return render(request, "core/import.html")
