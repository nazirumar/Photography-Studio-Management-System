from datetime import date

import pytest

from apps.clients.services import create_client
from apps.projects.models import Project, ProjectTask
from apps.projects.services import (
    create_project,
    create_task,
    generate_next_project_reference,
    update_project,
    update_project_status,
    update_task_status,
)
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


@pytest.mark.django_db
class TestProjectServices:
    def test_generate_next_reference(self, studio):
        assert generate_next_project_reference(studio) == "PRJ-0001"

    def test_generate_next_reference_subsequent(self, studio, user, client_obj):
        create_project(
            studio,
            {"client": client_obj, "reference": "PRJ-0005"},
            user,
        )
        assert generate_next_project_reference(studio) == "PRJ-0006"

    def test_create_project(self, studio, user, client_obj):
        project = create_project(
            studio,
            {
                "client": client_obj,
                "shoot_date": date(2026, 6, 15),
                "priority": "high",
            },
            user,
        )
        assert project.pk is not None
        assert project.reference == "PRJ-0001"
        assert project.status == Project.Status.SCHEDULED
        assert project.priority == "high"

    def test_create_project_audit_log(self, studio, user, client_obj):
        project = create_project(studio, {"client": client_obj}, user)
        from apps.audit.models import AuditLog

        log = AuditLog.objects.filter(
            entity_type="Project", entity_id=str(project.pk)
        ).latest("timestamp")
        assert log.action == "project_created"

    def test_update_project(self, studio, user, client_obj):
        project = create_project(studio, {"client": client_obj}, user)
        updated = update_project(project, {"priority": "urgent"}, user)
        assert updated.priority == "urgent"

    def test_update_project_status(self, studio, user, client_obj):
        project = create_project(studio, {"client": client_obj}, user)
        update_project_status(project, Project.Status.SHOOT_COMPLETED, user)
        project.refresh_from_db()
        assert project.status == Project.Status.SHOOT_COMPLETED

    def test_update_project_status_delivered_sets_date(self, studio, user, client_obj):
        project = create_project(studio, {"client": client_obj}, user)
        project.status = Project.Status.READY_FOR_DELIVERY
        project.save(update_fields=["status"])
        update_project_status(project, Project.Status.DELIVERED, user)
        project.refresh_from_db()
        assert project.actual_delivery is not None

    def test_create_task(self, studio, user, client_obj):
        project = create_project(studio, {"client": client_obj}, user)
        task = create_task(
            project,
            {"title": "Edit photos", "priority": "high"},
            user,
        )
        assert task.pk is not None
        assert task.title == "Edit photos"
        assert task.project == project

    def test_update_task_status(self, studio, user, client_obj):
        project = create_project(studio, {"client": client_obj}, user)
        task = create_task(project, {"title": "Test task"}, user)
        update_task_status(task, ProjectTask.Status.IN_PROGRESS, user)
        task.refresh_from_db()
        assert task.status == ProjectTask.Status.IN_PROGRESS

    def test_update_task_status_done_sets_date(self, studio, user, client_obj):
        project = create_project(studio, {"client": client_obj}, user)
        task = create_task(project, {"title": "Done task"}, user)
        update_task_status(task, ProjectTask.Status.DONE, user)
        task.refresh_from_db()
        assert task.completed_date is not None

    def test_multi_tenant_isolation(self, user):
        s1 = Studio.objects.create(name="Studio A")
        s2 = Studio.objects.create(name="Studio B")
        c1 = create_client(
            s1, {"client_number": "CLT-001", "first_name": "A", "last_name": "B"}, user
        )
        c2 = create_client(
            s2, {"client_number": "CLT-001", "first_name": "C", "last_name": "D"}, user
        )
        create_project(s1, {"client": c1}, user)
        create_project(s2, {"client": c2}, user)
        assert Project.objects.filter(studio=s1).count() == 1
        assert Project.objects.filter(studio=s2).count() == 1
