import pytest

from apps.clients.services import create_client
from apps.gallery.models import Gallery
from apps.gallery.services import (
    add_photo,
    add_photos_bulk,
    create_gallery,
    finalize_selection,
    get_selection_stats,
    toggle_photo_selection,
)
from apps.projects.services import create_project
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


@pytest.fixture
def client_obj(studio, user):
    return create_client(
        studio,
        {"client_number": "CLT-001", "first_name": "Test", "last_name": "Client"},
        user,
    )


@pytest.fixture
def project(studio, user, client_obj):
    return create_project(studio, {"client": client_obj}, user)


@pytest.mark.django_db
class TestGalleryServices:
    def test_create_gallery(self, project, user):
        gallery = create_gallery(
            project, {"name": "Final Edits", "is_selection": True}, user
        )
        assert gallery.pk is not None
        assert gallery.name == "Final Edits"
        assert gallery.project == project

    def test_create_gallery_audit_log(self, project, user):
        gallery = create_gallery(project, {"name": "Test"}, user)
        from apps.audit.models import AuditLog

        log = AuditLog.objects.filter(
            entity_type="Gallery", entity_id=str(gallery.pk)
        ).latest("timestamp")
        assert log.action == "gallery_created"

    def test_add_photo(self, project, user):
        gallery = create_gallery(project, {"name": "Test"}, user)
        photo = add_photo(
            gallery,
            {
                "file_name": "IMG_001.jpg",
                "storage_key": "uploads/test/IMG_001.jpg",
                "image_number": 1,
            },
            user,
        )
        assert photo.pk is not None
        assert photo.gallery == gallery

    def test_add_photos_bulk(self, project, user):
        gallery = create_gallery(project, {"name": "Bulk"}, user)
        photos_data = [
            {"file_name": f"IMG_{i:03d}.jpg", "storage_key": f"uploads/{i}.jpg", "image_number": i}
            for i in range(1, 6)
        ]
        count = add_photos_bulk(gallery, photos_data, user)
        assert count == 5
        assert gallery.photos.count() == 5

    def test_toggle_photo_selection(self, project, user, client_obj):
        gallery = create_gallery(project, {"name": "Sel"}, user)
        photo = add_photo(
            gallery,
            {"file_name": "IMG.jpg", "storage_key": "uploads/IMG.jpg", "image_number": 1},
            user,
        )
        selection = toggle_photo_selection(photo, client_obj, selected=True)
        assert selection.is_favourite is True
        project.refresh_from_db()
        assert project.selected_count == 1

    def test_toggle_photo_deselection(self, project, user, client_obj):
        gallery = create_gallery(project, {"name": "Sel"}, user)
        photo = add_photo(
            gallery,
            {"file_name": "IMG.jpg", "storage_key": "uploads/IMG.jpg", "image_number": 1},
            user,
        )
        toggle_photo_selection(photo, client_obj, selected=True)
        toggle_photo_selection(photo, client_obj, selected=False)
        project.refresh_from_db()
        assert project.selected_count == 0

    def test_finalize_selection(self, project, user, client_obj):
        gallery = create_gallery(project, {"name": "Final"}, user)
        photo = add_photo(
            gallery,
            {"file_name": "IMG.jpg", "storage_key": "uploads/IMG.jpg", "image_number": 1},
            user,
        )
        toggle_photo_selection(photo, client_obj, selected=True)
        count = finalize_selection(project, client_obj, user)
        assert count == 1
        project.refresh_from_db()
        assert project.status == "selection_received"

    def test_get_selection_stats(self, project, user, client_obj):
        gallery = create_gallery(project, {"name": "Stats"}, user)
        p1 = add_photo(
            gallery,
            {"file_name": "A.jpg", "storage_key": "a.jpg", "image_number": 1},
            user,
        )
        p2 = add_photo(
            gallery,
            {"file_name": "B.jpg", "storage_key": "b.jpg", "image_number": 2},
            user,
        )
        toggle_photo_selection(p1, client_obj, selected=True)
        toggle_photo_selection(p2, client_obj, selected=True)
        stats = get_selection_stats(project, client_obj)
        assert stats["favourites"] == 2
        assert stats["total_selections"] == 2

    def test_multi_tenant_isolation(self, user):
        s1 = Studio.objects.create(name="Studio A")
        s2 = Studio.objects.create(name="Studio B")
        c1 = create_client(
            s1, {"client_number": "CLT-001", "first_name": "A", "last_name": "B"}, user
        )
        c2 = create_client(
            s2, {"client_number": "CLT-001", "first_name": "C", "last_name": "D"}, user
        )
        p1 = create_project(s1, {"client": c1}, user)
        p2 = create_project(s2, {"client": c2}, user)
        create_gallery(p1, {"name": "G1"}, user)
        create_gallery(p2, {"name": "G2"}, user)
        assert Gallery.objects.filter(project__studio=s1).count() == 1
        assert Gallery.objects.filter(project__studio=s2).count() == 1
