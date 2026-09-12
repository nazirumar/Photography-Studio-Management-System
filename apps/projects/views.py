from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio
from apps.projects.forms import ProjectForm, ProjectSearchForm, TaskForm
from apps.projects.models import Project, ProjectTask
from apps.projects.services import (
    create_project,
    create_task,
    update_project,
    update_project_status,
    update_task_status,
)


@login_required
def project_list(request):
    studio = get_user_studio(request.user)
    form = ProjectSearchForm(request.GET or None)
    queryset = Project.objects.filter(studio=studio).select_related("client", "package")

    if form.is_valid():
        q = form.cleaned_data.get("q")
        status = form.cleaned_data.get("status")
        priority = form.cleaned_data.get("priority")
        if q:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(reference__icontains=q)
                | Q(client__first_name__icontains=q)
                | Q(client__last_name__icontains=q)
            )
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)

    paginator = Paginator(queryset, 20)
    page = request.GET.get("page")
    projects = paginator.get_page(page)

    return render(request, "projects/list.html", {
        "projects": projects,
        "form": form,
        "total_count": queryset.count(),
    })


@login_required
def project_create(request):
    studio = get_user_studio(request.user)
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.copy()
            project = create_project(studio=studio, data=data, user=request.user)
            messages.success(request, f"Project {project.reference} created.")
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, "projects/form.html", {"form": form, "title": "New Project"})


@login_required
def project_detail(request, pk):
    studio = get_user_studio(request.user)
    project = get_object_or_404(
        Project.objects.select_related("client", "package", "photographer"),
        pk=pk, studio=studio,
    )
    tasks = project.tasks.all()
    galleries = project.galleries.all()
    from apps.gallery.services import get_selection_stats
    selection_stats = get_selection_stats(project)
    return render(request, "projects/detail.html", {
        "project": project,
        "tasks": tasks,
        "galleries": galleries,
        "selection_stats": selection_stats,
    })


@login_required
def project_edit(request, pk):
    studio = get_user_studio(request.user)
    project = get_object_or_404(Project, pk=pk, studio=studio)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            update_project(project, form.cleaned_data, user=request.user)
            messages.success(request, f"Project {project.reference} updated.")
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, "projects/form.html", {"form": form, "title": "Edit Project", "project": project})


@login_required
def project_status_change(request, pk):
    studio = get_user_studio(request.user)
    project = get_object_or_404(Project, pk=pk, studio=studio)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status:
            try:
                update_project_status(project, new_status, user=request.user)
                messages.success(request, f"Project status updated to {new_status}.")
            except Exception as e:
                messages.error(request, str(e))
    return redirect("projects:detail", pk=pk)


@login_required
def task_create(request, pk):
    studio = get_user_studio(request.user)
    project = get_object_or_404(Project, pk=pk, studio=studio)
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            create_task(project, form.cleaned_data, user=request.user)
            messages.success(request, "Task created.")
    return redirect("projects:detail", pk=pk)


@login_required
def task_status_change(request, project_pk, task_pk):
    studio = get_user_studio(request.user)
    project = get_object_or_404(Project, pk=project_pk, studio=studio)
    task = get_object_or_404(ProjectTask, pk=task_pk, project=project)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status:
            update_task_status(task, new_status, user=request.user)
            messages.success(request, f"Task status updated to {new_status}.")
    return redirect("projects:detail", pk=project.pk)
