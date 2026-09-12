import pytest

from apps.clients.services import create_client
from apps.printing.models import AlbumOrder, FrameOrder, PrintJob
from apps.printing.services import (
    approve_album,
    create_album_order,
    create_frame_order,
    create_print_job,
    get_printing_summary,
    update_album_order_status,
    update_frame_order_status,
    update_print_job_status,
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
class TestPrintJobServices:
    def test_create_print_job(self, project, user):
        pj = create_print_job(
            project,
            {"print_size": "8x10", "quantity": 5, "paper_type": "Glossy"},
            user,
        )
        assert pj.pk is not None
        assert pj.print_size == "8x10"
        assert pj.quantity == 5
        assert pj.client == project.client

    def test_create_print_job_audit_log(self, project, user):
        pj = create_print_job(project, {"print_size": "5x7"}, user)
        from apps.audit.models import AuditLog

        log = AuditLog.objects.filter(
            entity_type="PrintJob", entity_id=str(pj.pk)
        ).latest("timestamp")
        assert log.action == "print_job_created"

    def test_update_print_job_status(self, project, user):
        pj = create_print_job(project, {"print_size": "8x10"}, user)
        update_print_job_status(pj, PrintJob.Status.PRINTING, user)
        pj.refresh_from_db()
        assert pj.status == PrintJob.Status.PRINTING

    def test_update_print_job_status_delivered(self, project, user):
        pj = create_print_job(project, {"print_size": "8x10"}, user)
        update_print_job_status(pj, PrintJob.Status.DELIVERED, user)
        pj.refresh_from_db()
        assert pj.status == PrintJob.Status.DELIVERED
        assert pj.completed_date is not None

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
        create_print_job(p1, {"print_size": "A4"}, user)
        create_print_job(p2, {"print_size": "A3"}, user)
        assert PrintJob.objects.filter(project__studio=s1).count() == 1
        assert PrintJob.objects.filter(project__studio=s2).count() == 1


@pytest.mark.django_db
class TestFrameOrderServices:
    def test_create_frame_order(self, project, user):
        frame = create_frame_order(
            project,
            {"size": "8x10", "frame_type": "Wood", "quantity": 2},
            user,
        )
        assert frame.pk is not None
        assert frame.size == "8x10"
        assert frame.quantity == 2

    def test_create_frame_order_audit_log(self, project, user):
        frame = create_frame_order(project, {"size": "5x7"}, user)
        from apps.audit.models import AuditLog

        log = AuditLog.objects.filter(
            entity_type="FrameOrder", entity_id=str(frame.pk)
        ).latest("timestamp")
        assert log.action == "frame_order_created"

    def test_update_frame_order_status(self, project, user):
        frame = create_frame_order(project, {"size": "8x10"}, user)
        update_frame_order_status(frame, FrameOrder.Status.ORDERED, user)
        frame.refresh_from_db()
        assert frame.status == FrameOrder.Status.ORDERED


@pytest.mark.django_db
class TestAlbumOrderServices:
    def test_create_album_order(self, project, user):
        album = create_album_order(
            project,
            {"size": "12x12", "pages": 30, "album_type": "Linen"},
            user,
        )
        assert album.pk is not None
        assert album.size == "12x12"
        assert album.pages == 30

    def test_create_album_order_audit_log(self, project, user):
        album = create_album_order(project, {"size": "10x10"}, user)
        from apps.audit.models import AuditLog

        log = AuditLog.objects.filter(
            entity_type="AlbumOrder", entity_id=str(album.pk)
        ).latest("timestamp")
        assert log.action == "album_order_created"

    def test_update_album_order_status(self, project, user):
        album = create_album_order(project, {"size": "12x12"}, user)
        update_album_order_status(album, AlbumOrder.Status.DESIGNING, user)
        album.refresh_from_db()
        assert album.design_status == AlbumOrder.Status.DESIGNING

    def test_approve_album(self, project, user):
        album = create_album_order(project, {"size": "12x12"}, user)
        approve_album(album, user)
        album.refresh_from_db()
        assert album.client_approved is True
        assert album.design_status == AlbumOrder.Status.PRODUCTION


@pytest.mark.django_db
class TestPrintingSummary:
    def test_get_printing_summary(self, project, user):
        create_print_job(project, {"print_size": "8x10"}, user)
        create_print_job(project, {"print_size": "5x7"}, user)
        create_frame_order(project, {"size": "8x10"}, user)
        summary = get_printing_summary(project.studio)
        assert summary["active_prints"] == 2
        assert summary["active_frames"] == 1
        assert summary["active_albums"] == 0
