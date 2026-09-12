from decimal import Decimal

import pytest

from apps.packages.models import Package, PackageAddon
from apps.packages.services import (
    create_package,
    create_service_category,
    get_package_addon_total,
    toggle_package_active,
    update_package,
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
class TestPackageServices:
    def test_create_package(self, studio, user):
        pkg = create_package(
            studio,
            {
                "name": "Basic Portrait",
                "price": Decimal("25000.00"),
                "deposit_percentage": Decimal("50.00"),
                "duration_hours": Decimal("1.0"),
                "outfit_changes": 1,
                "edited_images": 10,
            },
            user,
        )
        assert pkg.pk is not None
        assert pkg.name == "Basic Portrait"
        assert pkg.studio == studio

    def test_create_package_with_addons(self, studio, user):
        pkg = create_package(
            studio,
            {
                "name": "Wedding Package",
                "price": Decimal("150000.00"),
                "addons": [
                    {"name": "Extra album", "price": Decimal("30000.00")},
                    {"name": "Canvas print", "price": Decimal("15000.00")},
                ],
            },
            user,
        )
        assert pkg.addons.count() == 2
        assert pkg.addons.filter(name="Extra album").exists()

    def test_create_package_audit_log(self, studio, user):
        pkg = create_package(
            studio, {"name": "Test", "price": Decimal("10000.00")}, user
        )
        from apps.audit.models import AuditLog

        log = AuditLog.objects.filter(
            entity_type="Package", entity_id=str(pkg.pk)
        ).latest("timestamp")
        assert log.action == "package_created"

    def test_update_package(self, studio, user):
        pkg = create_package(
            studio, {"name": "Old", "price": Decimal("10000.00")}, user
        )
        updated = update_package(pkg, {"name": "New", "price": Decimal("20000.00")}, user)
        assert updated.name == "New"
        assert updated.price == Decimal("20000.00")

    def test_toggle_package_active(self, studio, user):
        pkg = create_package(
            studio, {"name": "T", "price": Decimal("10000.00"), "is_active": True}, user
        )
        toggled = toggle_package_active(pkg, user)
        assert toggled.is_active is False
        toggled2 = toggle_package_active(toggled, user)
        assert toggled2.is_active is True

    def test_get_package_addon_total(self, studio, user):
        pkg = create_package(
            studio, {"name": "P", "price": Decimal("10000.00")}, user
        )
        a1 = PackageAddon.objects.create(
            package=pkg, name="A1", price=Decimal("5000.00")
        )
        a2 = PackageAddon.objects.create(
            package=pkg, name="A2", price=Decimal("3000.00")
        )
        total = get_package_addon_total(pkg, [a1.pk, a2.pk])
        assert total == Decimal("18000.00")

    def test_create_service_category(self, studio, user):
        cat = create_service_category(
            studio, {"name": "Wedding Photography"}, user
        )
        assert cat.pk is not None
        assert cat.name == "Wedding Photography"

    def test_multi_tenant_isolation(self, user):
        s1 = Studio.objects.create(name="Studio A")
        s2 = Studio.objects.create(name="Studio B")
        create_package(s1, {"name": "P1", "price": Decimal("10000.00")}, user)
        create_package(s2, {"name": "P2", "price": Decimal("20000.00")}, user)
        assert Package.objects.filter(studio=s1).count() == 1
        assert Package.objects.filter(studio=s2).count() == 1
