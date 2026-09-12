import pytest

from apps.audit.models import AuditLog
from apps.audit.services import (
    get_action_summary,
    get_audit_logs,
    get_entity_history,
    get_entity_type_summary,
    get_user_activity,
)
from apps.studios.models import Studio


@pytest.fixture
def studio(db):
    return Studio.objects.create(name="Test Studio")


@pytest.fixture
def user(db):
    from django.contrib.auth import get_user_model
    return get_user_model().objects.create_user(
        email="test@studioflow.com", password="testpass123", first_name="T", last_name="U"
    )


@pytest.mark.django_db
class TestAuditLogRetrieval:
    def test_get_audit_logs_empty(self):
        logs = get_audit_logs()
        assert logs.count() == 0

    def test_get_audit_logs_with_data(self, user):
        AuditLog.objects.create(
            user=user, action="client_created", entity_type="Client", entity_id="abc-123"
        )
        logs = get_audit_logs()
        assert logs.count() == 1

    def test_get_audit_logs_by_entity_type(self, user):
        AuditLog.objects.create(user=user, action="created", entity_type="Client", entity_id="1")
        AuditLog.objects.create(user=user, action="created", entity_type="Booking", entity_id="2")
        logs = get_audit_logs(entity_type="Client")
        assert logs.count() == 1

    def test_get_audit_logs_by_user(self, user):
        AuditLog.objects.create(user=user, action="created", entity_type="Client", entity_id="1")
        logs = get_audit_logs(user=user)
        assert logs.count() == 1


@pytest.mark.django_db
class TestEntityHistory:
    def test_get_entity_history(self, user):
        AuditLog.objects.create(user=user, action="created", entity_type="Client", entity_id="abc")
        AuditLog.objects.create(user=user, action="updated", entity_type="Client", entity_id="abc")
        AuditLog.objects.create(user=user, action="created", entity_type="Client", entity_id="def")
        history = get_entity_history("Client", "abc")
        assert history.count() == 2

    def test_get_entity_history_empty(self):
        history = get_entity_history("Client", "nonexistent")
        assert history.count() == 0


@pytest.mark.django_db
class TestUserActivity:
    def test_get_user_activity(self, user):
        AuditLog.objects.create(user=user, action="created", entity_type="Client", entity_id="1")
        activity = get_user_activity(user)
        assert activity.count() == 1


@pytest.mark.django_db
class TestSummaries:
    def test_action_summary(self, user):
        AuditLog.objects.create(user=user, action="created", entity_type="Client", entity_id="1")
        AuditLog.objects.create(user=user, action="created", entity_type="Client", entity_id="2")
        AuditLog.objects.create(user=user, action="updated", entity_type="Client", entity_id="1")
        summary = get_action_summary()
        assert len(summary) == 2

    def test_entity_type_summary(self, user):
        AuditLog.objects.create(user=user, action="created", entity_type="Client", entity_id="1")
        AuditLog.objects.create(user=user, action="created", entity_type="Booking", entity_id="2")
        summary = get_entity_type_summary()
        assert len(summary) == 2
