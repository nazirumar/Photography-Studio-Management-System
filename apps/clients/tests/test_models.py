import pytest
from django.db import IntegrityError

from apps.clients.models import Client
from apps.studios.models import Studio


@pytest.mark.django_db
class TestClientModel:
    def _create_studio(self):
        return Studio.objects.create(name="Test Studio")

    def test_create_client(self):
        studio = self._create_studio()
        client = Client.objects.create(
            studio=studio,
            client_number="CLT-001",
            first_name="Aisha",
            last_name="Bello",
            phone="+2348012345678",
            email="aisha@example.com",
        )
        assert client.first_name == "Aisha"
        assert client.last_name == "Bello"
        assert client.display_name == "Aisha Bello"
        assert client.status == "active"

    def test_client_str(self):
        studio = self._create_studio()
        client = Client.objects.create(
            studio=studio,
            client_number="CLT-002",
            first_name="John",
            last_name="Doe",
        )
        assert str(client) == "John Doe"

    def test_client_unique_number_per_studio(self):
        studio = self._create_studio()
        Client.objects.create(studio=studio, client_number="CLT-001", first_name="A", last_name="B")
        with pytest.raises(IntegrityError):
            Client.objects.create(studio=studio, client_number="CLT-001", first_name="C", last_name="D")

    def test_client_different_studios_same_number(self):
        studio1 = Studio.objects.create(name="Studio 1")
        studio2 = Studio.objects.create(name="Studio 2")
        Client.objects.create(studio=studio1, client_number="CLT-001", first_name="A", last_name="B")
        client2 = Client.objects.create(studio=studio2, client_number="CLT-001", first_name="C", last_name="D")
        assert client2.client_number == "CLT-001"

    def test_client_save_auto_display_name(self):
        studio = self._create_studio()
        client = Client.objects.create(
            studio=studio,
            client_number="CLT-003",
            first_name="Fatima",
            last_name="Abubakar",
        )
        assert client.display_name == "Fatima Abubakar"
