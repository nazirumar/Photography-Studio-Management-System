import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import Role, StaffProfile

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert user.is_active is True
        assert user.is_staff is False

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
        )
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_user_str(self):
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assert str(user) == "test@example.com"

    def test_user_get_full_name(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        assert user.get_full_name() == "John Doe"

    def test_user_email_normalized(self):
        user = User.objects.create_user(email="TEST@EXAMPLE.COM", password="testpass123")
        assert user.email == "TEST@example.com"

    def test_user_requires_email(self):
        with pytest.raises(ValueError, match="Email is required"):
            User.objects.create_user(email="", password="testpass123")


@pytest.mark.django_db
class TestStaffProfile:
    def test_create_staff_profile(self, user):
        from apps.studios.models import Studio

        studio = Studio.objects.create(name="Test Studio")
        profile = StaffProfile.objects.create(
            user=user,
            studio=studio,
            role=Role.PHOTOGRAPHER,
            job_title="Senior Photographer",
        )
        assert profile.user == user
        assert profile.studio == studio
        assert profile.role == Role.PHOTOGRAPHER

    def test_staff_profile_str(self, user):
        from apps.studios.models import Studio

        studio = Studio.objects.create(name="Test Studio")
        user.first_name = "Jane"
        user.last_name = "Smith"
        user.save()
        profile = StaffProfile.objects.create(user=user, studio=studio, role=Role.ACCOUNTANT)
        assert "Jane Smith" in str(profile)
        assert "Accountant" in str(profile)

    def test_role_choices(self):
        assert Role.OWNER == "owner"
        assert Role.MANAGER == "manager"
        assert Role.RECEPTIONIST == "receptionist"
        assert Role.PHOTOGRAPHER == "photographer"
        assert Role.PHOTO_EDITOR == "photo_editor"
        assert Role.PRINTING_STAFF == "printing_staff"
        assert Role.ACCOUNTANT == "accountant"
