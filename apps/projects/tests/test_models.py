
import pytest
from django.utils import timezone

from apps.clients.models import Client
from apps.projects.models import Project, ProjectTask
from apps.studios.models import Studio


@pytest.mark.django_db
class TestProjectModel:
    def _setup(self):
        studio = Studio.objects.create(name="Test Studio")
        client = Client.objects.create(
            studio=studio, client_number="CLT-001", first_name="Test", last_name="Client"
        )
        return studio, client

    def test_create_project(self):
        studio, client = self._setup()
        project = Project.objects.create(
            studio=studio,
            reference="PRJ-001",
            client=client,
            status=Project.Status.SCHEDULED,
            shoot_date=timezone.now().date(),
        )
        assert project.reference == "PRJ-001"
        assert project.status == Project.Status.SCHEDULED

    def test_project_status_choices(self):
        assert Project.Status.EDITING == "editing"
        assert Project.Status.DELIVERED == "delivered"
        assert Project.Status.COMPLETED == "completed"

    def test_create_task(self):
        studio, client = self._setup()
        project = Project.objects.create(
            studio=studio, reference="PRJ-002", client=client
        )
        task = ProjectTask.objects.create(
            project=project,
            title="Backup RAW files",
            status=ProjectTask.Status.TODO,
        )
        assert task.title == "Backup RAW files"
        assert task.status == ProjectTask.Status.TODO
