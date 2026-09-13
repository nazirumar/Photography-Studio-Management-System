from rest_framework import serializers, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


# Booking Request API
class BookingRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    event_type = serializers.CharField(max_length=100)
    preferred_date = serializers.DateField()
    notes = serializers.CharField(required=False, allow_blank=True)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_booking_request_api(request):
    """API endpoint to create a booking request."""
    serializer = BookingRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    from apps.bookings.booking_request_service import create_booking_request
    from apps.accounts.services import get_user_studio
    
    studio = get_user_studio(request.user)
    booking_request = create_booking_request(studio, serializer.validated_data)
    
    return Response({
        "id": str(booking_request.pk),
        "status": booking_request.status,
        "message": "Booking request submitted successfully",
    }, status=status.HTTP_201_CREATED)


# Contract API
class ContractSerializer(serializers.Serializer):
    booking_id = serializers.UUIDField()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_contract_api(request):
    """API endpoint to create a contract for a booking."""
    serializer = ContractSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    from apps.bookings.models import Booking
    from apps.contracts.contract_service import create_contract
    from apps.accounts.services import get_user_studio
    
    studio = get_user_studio(request.user)
    booking = get_object_or_404(Booking, pk=serializer.validated_data["booking_id"], studio=studio)
    contract = create_contract(studio, booking, request.user)
    
    return Response({
        "id": str(contract.pk),
        "contract_number": contract.contract_number,
        "status": contract.status,
    }, status=status.HTTP_201_CREATED)


# Survey API
class SurveyResponseSerializer(serializers.Serializer):
    nps_score = serializers.IntegerField(min_value=0, max_value=10, required=False)
    overall_rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
    feedback_text = serializers.CharField(required=False, allow_blank=True)


@api_view(["POST"])
@permission_classes([])
def submit_survey_api(request, pk):
    """Public API endpoint to submit a survey response."""
    from apps.feedback.models import Survey
    from apps.feedback.feedback_service import submit_survey_response
    
    survey = get_object_or_404(Survey, pk=pk, is_completed=False)
    serializer = SurveyResponseSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    submit_survey_response(survey, serializer.validated_data)
    
    return Response({"message": "Thank you for your feedback!"})


# Supplier API
class SupplierSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    contact_person = serializers.CharField(max_length=200, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_supplier_api(request):
    """API endpoint to create a supplier."""
    serializer = SupplierSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    from apps.inventory.supplier_service import create_supplier
    from apps.accounts.services import get_user_studio
    
    studio = get_user_studio(request.user)
    supplier = create_supplier(studio, serializer.validated_data, request.user)
    
    return Response({
        "id": str(supplier.pk),
        "name": supplier.name,
    }, status=status.HTTP_201_CREATED)
