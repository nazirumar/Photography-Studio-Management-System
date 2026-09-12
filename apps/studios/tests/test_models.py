import pytest

from apps.studios.models import Studio


@pytest.mark.django_db
class TestStudioModel:
    def test_create_studio(self):
        studio = Studio.objects.create(
            name="Lagos Studio",
            phone="+2348012345678",
            email="info@lagosstudio.com",
            city="Lagos",
            state="Lagos",
            country="Nigeria",
            currency="NGN",
        )
        assert studio.name == "Lagos Studio"
        assert studio.currency == "NGN"
        assert studio.country == "Nigeria"
        assert studio.is_active is True

    def test_studio_str(self):
        studio = Studio.objects.create(name="Sunrise Photography")
        assert str(studio) == "Sunrise Photography"

    def test_studio_defaults(self):
        studio = Studio.objects.create(name="Default Studio")
        assert studio.currency == "NGN"
        assert studio.timezone == "Africa/Lagos"
        assert studio.invoice_prefix == "INV"
        assert studio.receipt_prefix == "RCT"
        assert studio.booking_prefix == "BKG"
        assert studio.project_prefix == "PRJ"
        assert studio.tax_rate == 0
        assert studio.default_deposit_percentage == 50
        assert studio.default_payment_terms == 30

    def test_studio_ordering(self):
        Studio.objects.create(name="Z Studio")
        Studio.objects.create(name="A Studio")
        studios = list(Studio.objects.values_list("name", flat=True))
        assert studios == ["A Studio", "Z Studio"]
