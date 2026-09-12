import pytest
from django.contrib.auth import get_user_model

from apps.audit.models import AuditLog

User = get_user_model()


@pytest.mark.django_db
class TestAuditLogModel:
    def test_create_audit_log(self):
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        log = AuditLog.objects.create(
            user=user,
            action="payment_created",
            entity_type="Payment",
            entity_id="pay-001",
            after_values={"amount": "100000"},
        )
        assert log.action == "payment_created"
        assert log.entity_type == "Payment"
        assert log.user == user

    def test_audit_log_str(self):
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        log = AuditLog.objects.create(
            user=user, action="booking_confirmed", entity_type="Booking", entity_id="bkg-001"
        )
        assert "booking_confirmed" in str(log)
