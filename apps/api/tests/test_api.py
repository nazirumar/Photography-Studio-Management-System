import pytest
from rest_framework.test import APIClient

from apps.studios.models import Studio


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    from django.contrib.auth import get_user_model
    return get_user_model().objects.create_user(
        email="test@studioflow.com", password="testpass123", first_name="T", last_name="U"
    )


@pytest.fixture
def studio(db):
    return Studio.objects.create(name="Test Studio")


@pytest.fixture
def auth_client(api_client, user, studio):
    user.studio = studio
    user.save(update_fields=["studio"])
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
class TestClientAPI:
    def test_list_clients(self, auth_client, studio, user):
        from apps.clients.services import create_client
        create_client(
            studio,
            {"client_number": "CLT-001", "first_name": "Test", "last_name": "Client"},
            user,
        )
        response = auth_client.get("/api/v1/clients/")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_create_client(self, auth_client, studio):
        response = auth_client.post("/api/v1/clients/", {
            "client_number": "CLT-002",
            "first_name": "New",
            "last_name": "Client",
            "email": "new@example.com",
        })
        assert response.status_code == 201


@pytest.mark.django_db
class TestBookingAPI:
    def test_list_bookings(self, auth_client):
        response = auth_client.get("/api/v1/bookings/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestDashboardAPI:
    def test_dashboard_stats(self, auth_client):
        response = auth_client.get("/api/v1/dashboard/")
        assert response.status_code == 200
        assert "monthly_revenue" in response.data
