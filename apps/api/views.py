from rest_framework import permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.accounts.services import get_user_studio
from apps.api.serializers import (
    BookingSerializer,
    ClientSerializer,
    InvoiceSerializer,
    PackageSerializer,
    PaymentSerializer,
    ProjectSerializer,
)
from apps.bookings.models import Booking
from apps.clients.models import Client
from apps.finance.models import Invoice, Payment
from apps.packages.models import Package
from apps.projects.models import Project


class IsStudioMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        studio = get_user_studio(request.user)
        if hasattr(obj, "studio"):
            return obj.studio == studio
        if hasattr(obj, "client") and hasattr(obj.client, "studio"):
            return obj.client.studio == studio
        return False


class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudioMember]

    def get_queryset(self):
        studio = get_user_studio(self.request.user)
        return Client.objects.filter(studio=studio)

    def perform_create(self, serializer):
        studio = get_user_studio(self.request.user)
        serializer.save(studio=studio)


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudioMember]

    def get_queryset(self):
        studio = get_user_studio(self.request.user)
        return Booking.objects.filter(studio=studio).select_related("client", "package")

    def perform_create(self, serializer):
        studio = get_user_studio(self.request.user)
        serializer.save(studio=studio)


class PackageViewSet(viewsets.ModelViewSet):
    serializer_class = PackageSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudioMember]

    def get_queryset(self):
        studio = get_user_studio(self.request.user)
        return Package.objects.filter(studio=studio)

    def perform_create(self, serializer):
        studio = get_user_studio(self.request.user)
        serializer.save(studio=studio)


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudioMember]

    def get_queryset(self):
        studio = get_user_studio(self.request.user)
        return Invoice.objects.filter(studio=studio).select_related("client")


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudioMember]

    def get_queryset(self):
        studio = get_user_studio(self.request.user)
        return Payment.objects.filter(studio=studio).select_related("client", "invoice")


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudioMember]

    def get_queryset(self):
        studio = get_user_studio(self.request.user)
        return Project.objects.filter(studio=studio).select_related("client")

    def perform_create(self, serializer):
        studio = get_user_studio(self.request.user)
        serializer.save(studio=studio)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """API endpoint for dashboard statistics."""
    from decimal import Decimal

    from django.db.models import Sum
    from django.utils import timezone

    from apps.expenses.models import Expense
    from apps.finance.models import Payment

    studio = get_user_studio(request.user)
    today = timezone.now().date()
    month_start = today.replace(day=1)

    revenue = Payment.objects.filter(
        invoice__booking__studio=studio, payment_date__gte=month_start
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    expenses = Expense.objects.filter(
        studio=studio, date__gte=month_start
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    return Response({
        "monthly_revenue": str(revenue),
        "monthly_expenses": str(expenses),
        "net_profit": str(revenue - expenses),
    })
