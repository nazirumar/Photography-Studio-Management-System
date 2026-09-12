from decimal import Decimal

import pytest

from apps.packages.models import Package, PackageAddon, ServiceCategory
from apps.studios.models import Studio


@pytest.mark.django_db
class TestPackageModel:
    def _create_studio(self):
        return Studio.objects.create(name="Test Studio")

    def test_create_package(self):
        studio = self._create_studio()
        pkg = Package.objects.create(
            studio=studio,
            name="Wedding Premium",
            price=Decimal("300000.00"),
            deposit_percentage=Decimal("50.00"),
            edited_images=50,
            extra_image_price=Decimal("1000.00"),
        )
        assert pkg.name == "Wedding Premium"
        assert pkg.price == Decimal("300000.00")
        assert pkg.edited_images == 50
        assert pkg.is_active is True

    def test_package_str(self):
        studio = self._create_studio()
        pkg = Package.objects.create(studio=studio, name="Birthday Session", price=Decimal("50000.00"))
        assert str(pkg) == "Birthday Session"

    def test_create_addon(self):
        studio = self._create_studio()
        pkg = Package.objects.create(studio=studio, name="Wedding", price=Decimal("300000.00"))
        addon = PackageAddon.objects.create(
            package=pkg,
            name="Extra Hour",
            price=Decimal("15000.00"),
        )
        assert addon.package == pkg
        assert addon.price == Decimal("15000.00")
        assert str(addon) == "Wedding - Extra Hour"

    def test_create_service_category(self):
        studio = self._create_studio()
        cat = ServiceCategory.objects.create(studio=studio, name="Wedding Photography")
        assert cat.name == "Wedding Photography"
        assert cat.is_active is True
        assert str(cat) == "Wedding Photography"
