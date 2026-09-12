from rest_framework import serializers

from apps.bookings.models import Booking
from apps.clients.models import Client
from apps.finance.models import Invoice, Payment
from apps.packages.models import Package
from apps.projects.models import Project


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "client_number", "first_name", "last_name", "email", "phone", "created_at"]


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ["id", "name", "description", "price", "duration_hours", "is_active"]


class BookingSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.__str__", read_only=True)
    package_name = serializers.CharField(source="package.__str__", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id", "reference", "client", "client_name", "package", "package_name",
            "title", "date", "start_time", "end_time", "status", "total_amount",
            "amount_paid", "payment_status", "created_at",
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.__str__", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id", "invoice_number", "client", "client_name", "issue_date", "due_date",
            "subtotal", "discount", "tax", "total", "amount_paid", "balance", "status",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.__str__", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id", "reference", "client", "client_name", "invoice", "amount",
            "payment_date", "method", "notes", "created_at",
        ]


class ProjectSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.__str__", read_only=True)

    class Meta:
        model = Project
        fields = [
            "id", "reference", "client", "client_name", "status",
            "shoot_date", "expected_delivery", "actual_delivery", "created_at",
        ]
