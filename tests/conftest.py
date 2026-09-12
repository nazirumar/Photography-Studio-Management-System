import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@studioflow.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        email="admin@studioflow.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
    )
