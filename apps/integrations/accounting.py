"""
Accounting integration module.
Supports QuickBooks and Xero export formats.
"""
import csv
import io


class QuickBooksExport:
    """Export financial data in QuickBooks-compatible CSV format."""

    @staticmethod
    def export_invoices(invoices):
        """Export invoices to QuickBooks CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # QuickBooks header
        writer.writerow([
            "Date", "Invoice No", "Customer Name", "Customer Email",
            "Item Description", "Quantity", "Rate", "Amount",
            "Tax", "Total", "Status", "Due Date"
        ])

        for invoice in invoices:
            for item in invoice.items.all():
                writer.writerow([
                    invoice.issue_date.strftime("%m/%d/%Y"),
                    invoice.invoice_number,
                    str(invoice.client),
                    invoice.client.email,
                    item.description,
                    float(item.quantity),
                    float(item.unit_price),
                    float(item.total),
                    float(invoice.tax),
                    float(invoice.total),
                    invoice.get_status_display(),
                    invoice.due_date.strftime("%m/%d/%Y") if invoice.due_date else "",
                ])

        return output.getvalue()

    @staticmethod
    def export_payments(payments):
        """Export payments to QuickBooks CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Date", "Reference", "Customer Name", "Amount",
            "Method", "Invoice No", "Notes"
        ])

        for payment in payments:
            writer.writerow([
                payment.payment_date.strftime("%m/%d/%Y"),
                payment.reference,
                str(payment.client),
                float(payment.amount),
                payment.get_method_display(),
                payment.invoice.invoice_number if payment.invoice else "",
                payment.notes,
            ])

        return output.getvalue()


class XeroExport:
    """Export financial data in Xero-compatible CSV format."""

    @staticmethod
    def export_invoices(invoices):
        """Export invoices to Xero CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Invoice Number", "Contact Name", "Date", "Due Date",
            "Line Item Description", "Quantity", "Unit Price", "Line Amount",
            "Invoice Total", "Amount Paid", "Balance", "Status", "Currency"
        ])

        for invoice in invoices:
            for item in invoice.items.all():
                writer.writerow([
                    invoice.invoice_number,
                    str(invoice.client),
                    invoice.issue_date.isoformat(),
                    invoice.due_date.isoformat() if invoice.due_date else "",
                    item.description,
                    float(item.quantity),
                    float(item.unit_price),
                    float(item.total),
                    float(invoice.total),
                    float(invoice.amount_paid),
                    float(invoice.balance),
                    invoice.get_status_display(),
                    "NGN",
                ])

        return output.getvalue()


def get_export_formats():
    """Return available export formats."""
    return {
        "quickbooks": {
            "name": "QuickBooks",
            "extensions": ["csv"],
            "exports": ["invoices", "payments"],
        },
        "xero": {
            "name": "Xero",
            "extensions": ["csv"],
            "exports": ["invoices"],
        },
    }
