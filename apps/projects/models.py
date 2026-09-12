from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class Project(BaseModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        SHOOT_COMPLETED = "shoot_completed", "Shoot Completed"
        FILES_IMPORTED = "files_imported", "Files Imported"
        AWAITING_SELECTION = "awaiting_selection", "Awaiting Client Selection"
        SELECTION_RECEIVED = "selection_received", "Selection Received"
        EDITING = "editing", "Editing"
        EDITING_REVIEW = "editing_review", "Editing Review"
        READY_FOR_PRINT = "ready_for_print", "Ready For Print"
        PRINTING = "printing", "Printing"
        QUALITY_CONTROL = "quality_control", "Quality Control"
        READY_FOR_DELIVERY = "ready_for_delivery", "Ready For Delivery"
        DELIVERED = "delivered", "Delivered"
        COMPLETED = "completed", "Completed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    studio = models.ForeignKey("studios.Studio", on_delete=models.CASCADE, related_name="projects")
    reference = models.CharField(max_length=50)
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="projects")
    booking = models.OneToOneField(
        "bookings.Booking", on_delete=models.SET_NULL, null=True, blank=True, related_name="project"
    )
    package = models.ForeignKey("packages.Package", on_delete=models.SET_NULL, null=True, blank=True)
    photographer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="photographer_projects",
    )
    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="editor_projects",
    )
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="managed_projects",
    )
    shoot_date = models.DateField(null=True, blank=True)
    expected_delivery = models.DateField(null=True, blank=True)
    actual_delivery = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.SCHEDULED)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    total_captured = models.IntegerField(default=0)
    total_for_selection = models.IntegerField(default=0)
    selected_count = models.IntegerField(default=0)
    edited_count = models.IntegerField(default=0)
    printed_count = models.IntegerField(default=0)
    internal_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("studio", "reference")]

    def __str__(self):
        return f"{self.reference} - {self.client}"

class ProjectTask(BaseModel):
    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        BLOCKED = "blocked", "Blocked"
        DONE = "done", "Done"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="project_tasks",
    )
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=Project.Priority.choices, default=Project.Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    completed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["due_date", "-priority"]

    def __str__(self):
        return self.title
