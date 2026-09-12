import os
import uuid

from PIL import Image

from django.conf import settings
from django.db import transaction

from apps.audit.models import AuditLog
from apps.gallery.models import Gallery, Photo, PhotoSelection


def create_gallery(project, data, user):
    """Create a gallery for a project."""
    with transaction.atomic():
        gallery = Gallery.objects.create(project=project, **data)
        AuditLog.objects.create(
            user=user,
            action="gallery_created",
            entity_type="Gallery",
            entity_id=str(gallery.id),
            after_values={"name": gallery.name, "project": project.reference},
        )
        return gallery


def add_photo(gallery, data, user):
    """Add a photo to a gallery."""
    with transaction.atomic():
        photo = Photo.objects.create(gallery=gallery, **data)
        project = gallery.project
        project.total_captured = Photo.objects.filter(gallery__project=project).count()
        project.save(update_fields=["total_captured", "updated_at"])
        return photo


def add_photos_bulk(gallery, photos_data, user):
    """Add multiple photos to a gallery at once."""
    with transaction.atomic():
        photos = []
        for data in photos_data:
            photos.append(Photo(gallery=gallery, **data))
        Photo.objects.bulk_create(photos)
        project = gallery.project
        project.total_captured = Photo.objects.filter(gallery__project=project).count()
        project.save(update_fields=["total_captured", "updated_at"])
        return len(photos)


def toggle_photo_selection(photo, client, selected=True):
    """Toggle photo selection for a client."""
    with transaction.atomic():
        selection, created = PhotoSelection.objects.get_or_create(
            photo=photo, client=client,
            defaults={"is_favourite": selected},
        )
        if not created:
            selection.is_favourite = selected
            selection.save(update_fields=["is_favourite", "updated_at"])

        project = photo.gallery.project
        project.selected_count = PhotoSelection.objects.filter(
            photo__gallery__project=project, client=client, is_favourite=True
        ).count()
        project.save(update_fields=["selected_count", "updated_at"])
        return selection


def finalize_selection(project, client, user):
    """Finalize client photo selection."""
    with transaction.atomic():
        selections = PhotoSelection.objects.filter(
            photo__gallery__project=project, client=client, is_favourite=True
        )
        selections.update(finalized=True)
        project.selected_count = selections.count()
        project.status = "selection_received"
        project.save(update_fields=["selected_count", "status", "updated_at"])
        AuditLog.objects.create(
            user=user,
            action="selection_finalized",
            entity_type="Project",
            entity_id=str(project.id),
            after_values={"selected_count": project.selected_count},
        )
        return selections.count()


def get_selection_stats(project, client=None):
    """Get selection statistics for a project."""
    qs = PhotoSelection.objects.filter(photo__gallery__project=project)
    if client:
        qs = qs.filter(client=client)

    total = qs.count()
    favourites = qs.filter(is_favourite=True).count()
    finalized = qs.filter(finalized=True).count()

    return {
        "total_selections": total,
        "favourites": favourites,
        "finalized": finalized,
    }


def generate_thumbnail(image_path, size=(200, 200)):
    """Create a thumbnail from an image file."""
    thumb_dir = os.path.join(settings.MEDIA_ROOT, "thumbnails")
    os.makedirs(thumb_dir, exist_ok=True)

    ext = os.path.splitext(image_path)[1]
    thumb_name = f"{uuid.uuid4().hex}{ext}"
    thumb_path = os.path.join(thumb_dir, thumb_name)

    with Image.open(image_path) as img:
        img.thumbnail(size, Image.LANCZOS)
        if img.mode in ("RGBA", "LA"):
            img = img.convert("RGB")
        img.save(thumb_path, quality=85, optimize=True)

    return f"thumbnails/{thumb_name}"


def generate_preview(image_path, size=(800, 800)):
    """Create a preview-sized image."""
    preview_dir = os.path.join(settings.MEDIA_ROOT, "previews")
    os.makedirs(preview_dir, exist_ok=True)

    ext = os.path.splitext(image_path)[1]
    preview_name = f"{uuid.uuid4().hex}{ext}"
    preview_path = os.path.join(preview_dir, preview_name)

    with Image.open(image_path) as img:
        img.thumbnail(size, Image.LANCZOS)
        if img.mode in ("RGBA", "LA"):
            img = img.convert("RGB")
        img.save(preview_path, quality=85, optimize=True)

    return f"previews/{preview_name}"


def process_upload(file, studio, project):
    """Save uploaded file, generate thumbnail and preview, return Photo object."""
    media_dir = os.path.join(settings.MEDIA_ROOT, "uploads", project.reference)
    os.makedirs(media_dir, exist_ok=True)

    ext = os.path.splitext(file.name)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(media_dir, unique_name)

    with open(file_path, "wb") as f:
        for chunk in file.chunks():
            f.write(chunk)

    thumbnail_key = generate_thumbnail(file_path)
    preview_key = generate_preview(file_path)

    gallery = project.galleries.first()
    if not gallery:
        gallery = Gallery.objects.create(project=project, name="Default")

    photo = Photo.objects.create(
        gallery=gallery,
        file_name=unique_name,
        original_file_name=file.name,
        storage_key=f"uploads/{project.reference}/{unique_name}",
        thumbnail_key=thumbnail_key,
        preview_key=preview_key,
        image_number=gallery.photos.count() + 1,
    )

    project.total_captured = Photo.objects.filter(gallery__project=project).count()
    project.save(update_fields=["total_captured", "updated_at"])

    return photo


def batch_upload(files, gallery):
    """Upload multiple files to a gallery."""
    project = gallery.project
    media_dir = os.path.join(settings.MEDIA_ROOT, "uploads", project.reference)
    os.makedirs(media_dir, exist_ok=True)

    photos = []
    for f in files:
        ext = os.path.splitext(f.name)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(media_dir, unique_name)

        with open(file_path, "wb") as out:
            for chunk in f.chunks():
                out.write(chunk)

        thumbnail_key = generate_thumbnail(file_path)
        preview_key = generate_preview(file_path)

        photos.append(Photo(
            gallery=gallery,
            file_name=unique_name,
            original_file_name=f.name,
            storage_key=f"uploads/{project.reference}/{unique_name}",
            thumbnail_key=thumbnail_key,
            preview_key=preview_key,
            image_number=gallery.photos.count() + len(photos) + 1,
        ))

    Photo.objects.bulk_create(photos)

    project.total_captured = Photo.objects.filter(gallery__project=project).count()
    project.save(update_fields=["total_captured", "updated_at"])

    return len(photos)
