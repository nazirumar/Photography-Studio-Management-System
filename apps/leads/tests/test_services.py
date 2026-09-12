import pytest

from apps.leads.models import Lead
from apps.leads.services import (
    convert_lead_to_client,
    create_lead,
    get_lead_pipeline_counts,
    update_lead,
    update_lead_status,
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
class TestLeadServices:
    def test_create_lead(self, studio, user):
        lead = create_lead(
            studio,
            {
                "name": "Amina Yusuf",
                "phone": "+2348098765432",
                "event_type": "Wedding",
                "source": "Instagram",
                "status": Lead.Status.NEW,
            },
            user,
        )
        assert lead.pk is not None
        assert lead.status == Lead.Status.NEW
        assert lead.name == "Amina Yusuf"

    def test_create_lead_audit_log(self, studio, user):
        lead = create_lead(studio, {"name": "Test", "status": Lead.Status.NEW}, user)
        from apps.audit.models import AuditLog

        log = AuditLog.objects.filter(
            entity_type="Lead", entity_id=str(lead.pk)
        ).latest("timestamp")
        assert log.action == "lead_created"

    def test_update_lead(self, studio, user):
        lead = create_lead(
            studio, {"name": "Old", "status": Lead.Status.NEW}, user
        )
        updated = update_lead(
            lead, {"name": "New", "status": Lead.Status.CONTACTED}, user
        )
        assert updated.name == "New"
        assert updated.status == Lead.Status.CONTACTED

    def test_update_lead_status(self, studio, user):
        lead = create_lead(studio, {"name": "X", "status": Lead.Status.NEW}, user)
        update_lead_status(lead, Lead.Status.FOLLOW_UP, user)
        lead.refresh_from_db()
        assert lead.status == Lead.Status.FOLLOW_UP

    def test_convert_lead_to_client(self, studio, user):
        lead = create_lead(
            studio,
            {
                "name": "Bola Adekunle",
                "phone": "+2348011112222",
                "email": "bola@test.com",
                "source": "Referral",
                "status": Lead.Status.NEGOTIATING,
            },
            user,
        )
        client = convert_lead_to_client(lead, user)
        assert client.pk is not None
        assert client.first_name == "Bola"
        assert client.last_name == "Adekunle"
        assert client.phone == "+2348011112222"
        assert client.studio == studio
        lead.refresh_from_db()
        assert lead.status == Lead.Status.WON
        assert lead.converted_client == client

    def test_convert_single_name_lead(self, studio, user):
        lead = create_lead(
            studio, {"name": "Ngozi", "status": Lead.Status.NEW}, user
        )
        client = convert_lead_to_client(lead, user)
        assert client.first_name == "Ngozi"
        assert client.last_name == ""

    def test_get_lead_pipeline_counts(self, studio, user):
        create_lead(studio, {"name": "L1", "status": Lead.Status.NEW}, user)
        create_lead(studio, {"name": "L2", "status": Lead.Status.NEW}, user)
        create_lead(studio, {"name": "L3", "status": Lead.Status.WON}, user)
        pipeline = get_lead_pipeline_counts(studio)
        counts = {item["status"]: item["count"] for item in pipeline}
        assert counts[Lead.Status.NEW] == 2
        assert counts[Lead.Status.WON] == 1

    def test_multi_tenant_isolation(self, user):
        s1 = Studio.objects.create(name="Studio A")
        s2 = Studio.objects.create(name="Studio B")
        create_lead(s1, {"name": "Lead 1", "status": Lead.Status.NEW}, user)
        create_lead(s2, {"name": "Lead 2", "status": Lead.Status.NEW}, user)
        assert Lead.objects.filter(studio=s1).count() == 1
        assert Lead.objects.filter(studio=s2).count() == 1

    def test_lead_won_cannot_convert_again(self, studio, user):
        lead = create_lead(
            studio, {"name": "Done", "status": Lead.Status.WON}, user
        )
        assert lead.status == Lead.Status.WON
