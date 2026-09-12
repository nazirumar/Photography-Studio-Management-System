from django.contrib import admin
from .models import Project, ProjectTask


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("reference", "client", "status", "priority", "shoot_date", "expected_delivery", "studio")
    list_filter = ("status", "priority", "studio")
    search_fields = ("reference", "client__first_name", "client__last_name")
    date_hierarchy = "shoot_date"


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "assigned_to", "status", "due_date")
    list_filter = ("status", "project")
    search_fields = ("title",)
