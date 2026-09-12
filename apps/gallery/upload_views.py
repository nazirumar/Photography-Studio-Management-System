from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio
from apps.gallery.models import Gallery, Photo
from apps.gallery.services import batch_upload


@login_required
def upload_photos(request, gallery_pk):
    studio = get_user_studio(request.user)
    gallery = get_object_or_404(
        Gallery.objects.select_related("project"),
        pk=gallery_pk, project__studio=studio,
    )
    if request.method == "POST":
        files = request.FILES.getlist("files")
        if files:
            count = batch_upload(files, gallery)
            messages.success(request, f"{count} photo(s) uploaded successfully.")
            if request.headers.get("HX-Request"):
                return render(request, "gallery/_photo_grid.html", {
                    "gallery": gallery,
                    "photos": gallery.photos.all(),
                })
            return redirect("gallery:detail", project_pk=gallery.project.pk, pk=gallery.pk)
        messages.error(request, "No files selected.")
    return render(request, "gallery/upload.html", {"gallery": gallery})


@login_required
def delete_photo(request, pk):
    studio = get_user_studio(request.user)
    photo = get_object_or_404(
        Photo.objects.select_related("gallery__project"),
        pk=pk, gallery__project__studio=studio,
    )
    if request.method == "POST":
        gallery = photo.gallery
        project = gallery.project
        photo.delete()
        project.total_captured = Photo.objects.filter(gallery__project=project).count()
        project.save(update_fields=["total_captured", "updated_at"])
        messages.success(request, "Photo deleted.")
        if request.headers.get("HX-Request"):
            return render(request, "gallery/_photo_grid.html", {
                "gallery": gallery,
                "photos": gallery.photos.all(),
            })
        return redirect("gallery:detail", project_pk=project.pk, pk=gallery.pk)
    return redirect("gallery:detail", project_pk=photo.gallery.project.pk, pk=photo.gallery.pk)
