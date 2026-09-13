from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio
from apps.gallery.forms import GalleryForm
from apps.gallery.models import Gallery, Photo
from apps.gallery.services import (
    add_photos_bulk,
    create_gallery,
    finalize_selection,
    get_selection_stats,
    toggle_photo_selection,
)
from apps.projects.models import Project


@login_required
def gallery_list(request, project_pk):
    studio = get_user_studio(request.user)
    project = get_object_or_404(Project, pk=project_pk, studio=studio)
    galleries = project.galleries.all()
    return render(request, "gallery/list.html", {
        "project": project,
        "galleries": galleries,
    })


@login_required
def gallery_create(request, project_pk):
    studio = get_user_studio(request.user)
    project = get_object_or_404(Project, pk=project_pk, studio=studio)
    if request.method == "POST":
        form = GalleryForm(request.POST)
        if form.is_valid():
            gallery = create_gallery(project, form.cleaned_data, user=request.user)
            messages.success(request, f"Gallery {gallery.name} created.")
            return redirect("gallery:detail", project_pk=project.pk, pk=gallery.pk)
    else:
        form = GalleryForm()
    return render(request, "gallery/form.html", {
        "form": form, "title": "New Gallery", "project": project,
    })


@login_required
def gallery_detail(request, project_pk, pk):
    studio = get_user_studio(request.user)
    project = get_object_or_404(Project, pk=project_pk, studio=studio)
    gallery = get_object_or_404(Gallery, pk=pk, project=project)
    photos = gallery.photos.all()
    return render(request, "gallery/detail.html", {
        "project": project,
        "gallery": gallery,
        "photos": photos,
    })


@login_required
def photo_upload(request, project_pk, gallery_pk):
    studio = get_user_studio(request.user)
    project = get_object_or_404(Project, pk=project_pk, studio=studio)
    gallery = get_object_or_404(Gallery, pk=gallery_pk, project=project)
    if request.method == "POST":
        files = request.FILES.getlist("files")
        if files:
            photos_data = []
            for i, f in enumerate(files, start=gallery.photos.count() + 1):
                photos_data.append({
                    "file_name": f.name,
                    "original_file_name": f.name,
                    "storage_key": f"uploads/{project.reference}/{gallery.name}/{f.name}",
                    "image_number": i,
                })
            count = add_photos_bulk(gallery, photos_data, user=request.user)
            messages.success(request, f"{count} photos uploaded.")
    return redirect("gallery:detail", project_pk=project.pk, pk=gallery.pk)


@login_required
def photo_toggle_selection(request, project_pk, gallery_pk, photo_pk):
    studio = get_user_studio(request.user)
    project = get_object_or_404(Project, pk=project_pk, studio=studio)
    photo = get_object_or_404(Photo.objects.select_related("gallery"), pk=photo_pk, gallery__project=project)
    if request.method == "POST":
        selected = request.POST.get("selected") == "true"
        client = project.client
        toggle_photo_selection(photo, client, selected=selected)
    return redirect("gallery:detail", project_pk=project.pk, pk=photo.gallery.pk)


@login_required
def selection_finalize(request, project_pk):
    studio = get_user_studio(request.user)
    project = get_object_or_404(Project, pk=project_pk, studio=studio)
    if request.method == "POST":
        client = project.client
        count = finalize_selection(project, client, user=request.user)
        messages.success(request, f"Selection finalized with {count} photos.")
    return redirect("projects:detail", pk=project.pk)


@login_required
def selection_stats(request, project_pk):
    studio = get_user_studio(request.user)
    project = get_object_or_404(Project, pk=project_pk, studio=studio)
    stats = get_selection_stats(project)
    return render(request, "gallery/selection_stats.html", {
        "project": project,
        "stats": stats,
    })
