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
