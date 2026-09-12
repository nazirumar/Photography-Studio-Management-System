from datetime import date

import pytest

from apps.equipment.models import Equipment
from apps.equipment.services import (
    assign_equipment,
    create_equipment,
    get_available_equipment,
    get_maintenance_due,
    update_equipment,
    update_equipment_status,
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
class TestEquipmentServices:
    def test_create_equipment(self, studio, user):
        eq = create_equipment(
            studio,
            {
                "asset_number": "EQ-001",
                "name": "Canon 5D Mark IV",
                "brand": "Canon",
                "status": Equipment.Status.AVAILABLE,
            },
            user,
        )
        assert eq.pk is not None
        assert eq.asset_number == "EQ-001"

    def test_create_equipment_audit_log(self, studio, user):
        eq = create_equipment(
            studio, {"asset_number": "EQ-002", "name": "Test"}, user
        )
        from apps.audit.models import AuditLog

        log = AuditLog.objects.filter(
            entity_type="Equipment", entity_id=str(eq.pk)
        ).latest("timestamp")
        assert log.action == "equipment_created"

    def test_update_equipment(self, studio, user):
        eq = create_equipment(
            studio, {"asset_number": "EQ-003", "name": "Old"}, user
        )
        updated = update_equipment(eq, {"name": "New", "brand": "Nikon"}, user)
        assert updated.name == "New"
        assert updated.brand == "Nikon"

    def test_update_equipment_status(self, studio, user):
        eq = create_equipment(
            studio, {"asset_number": "EQ-004", "name": "Test"}, user
        )
        update_equipment_status(eq, Equipment.Status.MAINTENANCE, user)
        eq.refresh_from_db()
        assert eq.status == Equipment.Status.MAINTENANCE

    def test_assign_equipment(self, studio, user):
        eq = create_equipment(
            studio, {"asset_number": "EQ-005", "name": "Test"}, user
        )
        assign_equipment(eq, user, user)
        eq.refresh_from_db()
        assert eq.assigned_to == user
        assert eq.status == Equipment.Status.IN_USE

    def test_unassign_equipment(self, studio, user):
        eq = create_equipment(
            studio, {"asset_number": "EQ-006", "name": "Test"}, user
        )
        assign_equipment(eq, user, user)
        assign_equipment(eq, None, user)
        eq.refresh_from_db()
        assert eq.assigned_to is None
        assert eq.status == Equipment.Status.AVAILABLE

    def test_get_available_equipment(self, studio, user):
        create_equipment(
            studio, {"asset_number": "A-001", "name": "Available", "status": Equipment.Status.AVAILABLE}, user
        )
        create_equipment(
            studio, {"asset_number": "A-002", "name": "In Use", "status": Equipment.Status.IN_USE}, user
        )
        available = get_available_equipment(studio)
        assert available.count() == 1
        assert available.first().asset_number == "A-001"

    def test_get_maintenance_due(self, studio, user):
        create_equipment(
            studio,
            {
                "asset_number": "M-001",
                "name": "Due",
                "next_maintenance": date(2020, 1, 1),
                "status": Equipment.Status.AVAILABLE,
            },
            user,
        )
        create_equipment(
            studio,
            {
                "asset_number": "M-002",
                "name": "Not Due",
                "next_maintenance": date(2099, 1, 1),
                "status": Equipment.Status.AVAILABLE,
            },
            user,
        )
        due = get_maintenance_due(studio)
        assert due.count() == 1
        assert due.first().asset_number == "M-001"

    def test_multi_tenant_isolation(self, user):
        s1 = Studio.objects.create(name="Studio A")
        s2 = Studio.objects.create(name="Studio B")
        create_equipment(s1, {"asset_number": "A-001", "name": "A"}, user)
        create_equipment(s2, {"asset_number": "B-001", "name": "B"}, user)
        assert Equipment.objects.filter(studio=s1).count() == 1
        assert Equipment.objects.filter(studio=s2).count() == 1
