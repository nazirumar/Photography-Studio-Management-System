import pytest

from apps.studios.models import Studio


@pytest.fixture
def studio(db):
    return Studio.objects.create(name="Test Studio")


@pytest.fixture
def user(db):
    from django.contrib.auth import get_user_model
    return get_user_model().objects.create_user(
        email="client@test.com", password="testpass123", first_name="Test", last_name="Client"
    )


@pytest.fixture
def client_obj(studio, user):
    from apps.clients.services import create_client
    return create_client(
        studio,
        {"client_number": "CLT-001", "first_name": "Test", "last_name": "Client", "email": "client@test.com"},
        user,
    )


@pytest.mark.django_db
class TestPortal:
    def test_portal_dashboard(self, user, client_obj):
        from django.test import Client
        c = Client()
        c.login(email="client@test.com", password="testpass123")
        response = c.get("/portal/")
        assert response.status_code == 200

    def test_portal_bookings(self, user, client_obj):
        from django.test import Client
        c = Client()
        c.login(email="client@test.com", password="testpass123")
        response = c.get("/portal/bookings/")
        assert response.status_code == 200

    def test_portal_invoices(self, user, client_obj):
        from django.test import Client
        c = Client()
        c.login(email="client@test.com", password="testpass123")
        response = c.get("/portal/invoices/")
        assert response.status_code == 200

    def test_portal_galleries(self, user, client_obj):
        from django.test import Client
        c = Client()
        c.login(email="client@test.com", password="testpass123")
        response = c.get("/portal/galleries/")
        assert response.status_code == 200
