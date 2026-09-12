from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.printing.models import AlbumOrder, FrameOrder, PrintJob


def create_print_job(project, data, user):
    """Create a new print job."""
    with transaction.atomic():
        print_job = PrintJob.objects.create(project=project, client=project.client, **data)
        AuditLog.objects.create(
            user=user,
            action="print_job_created",
            entity_type="PrintJob",
            entity_id=str(print_job.id),
            after_values={
                "print_size": print_job.print_size,
                "quantity": print_job.quantity,
                "project": project.reference,
            },
        )
        return print_job


def update_print_job_status(print_job, new_status, user):
    """Update print job status."""
    with transaction.atomic():
        old_status = print_job.status
        print_job.status = new_status
        if new_status == PrintJob.Status.DELIVERED:
            print_job.completed_date = timezone.now().date()
        print_job.save(update_fields=["status", "completed_date", "updated_at"])
        AuditLog.objects.create(
            user=user,
            action="print_job_status_changed",
            entity_type="PrintJob",
            entity_id=str(print_job.id),
            before_values={"status": old_status},
            after_values={"status": new_status},
        )
        return print_job


def create_frame_order(project, data, user):
    """Create a new frame order."""
    with transaction.atomic():
        frame = FrameOrder.objects.create(project=project, **data)
        AuditLog.objects.create(
            user=user,
            action="frame_order_created",
            entity_type="FrameOrder",
            entity_id=str(frame.id),
            after_values={"size": frame.size, "project": project.reference},
        )
        return frame


def update_frame_order_status(frame, new_status, user):
    """Update frame order status."""
    with transaction.atomic():
        old_status = frame.status
        frame.status = new_status
        frame.save(update_fields=["status", "updated_at"])
        AuditLog.objects.create(
            user=user,
            action="frame_order_status_changed",
            entity_type="FrameOrder",
            entity_id=str(frame.id),
            before_values={"status": old_status},
            after_values={"status": new_status},
        )
        return frame


def create_album_order(project, data, user):
    """Create a new album order."""
    with transaction.atomic():
        album = AlbumOrder.objects.create(project=project, **data)
        AuditLog.objects.create(
            user=user,
            action="album_order_created",
            entity_type="AlbumOrder",
            entity_id=str(album.id),
            after_values={"size": album.size, "project": project.reference},
        )
        return album


def update_album_order_status(album, new_status, user):
    """Update album order status."""
    with transaction.atomic():
        old_status = album.design_status
        album.design_status = new_status
        album.save(update_fields=["design_status", "updated_at"])
        AuditLog.objects.create(
            user=user,
            action="album_order_status_changed",
            entity_type="AlbumOrder",
            entity_id=str(album.id),
            before_values={"design_status": old_status},
            after_values={"design_status": new_status},
        )
        return album


def approve_album(album, user):
    """Client approve album order."""
    with transaction.atomic():
        album.client_approved = True
        album.design_status = AlbumOrder.Status.PRODUCTION
        album.save(update_fields=["client_approved", "design_status", "updated_at"])
        AuditLog.objects.create(
            user=user,
            action="album_approved",
            entity_type="AlbumOrder",
            entity_id=str(album.id),
            after_values={"client_approved": True},
        )
        return album


def get_printing_summary(studio):
    """Get printing summary for a studio."""
    from django.db.models import Sum

    print_jobs = PrintJob.objects.filter(project__studio=studio)
    frame_orders = FrameOrder.objects.filter(project__studio=studio)
    album_orders = AlbumOrder.objects.filter(project__studio=studio)

    active_prints = print_jobs.exclude(status__in=["delivered"]).count()
    active_frames = frame_orders.exclude(status__in=["delivered"]).count()
    active_albums = album_orders.exclude(design_status__in=["delivered"]).count()

    total_print_cost = print_jobs.aggregate(
        total=Sum("internal_cost")
    )["total"] or 0
    total_frame_cost = frame_orders.aggregate(
        total=Sum("internal_cost")
    )["total"] or 0
    total_album_cost = album_orders.aggregate(
        total=Sum("cost")
    )["total"] or 0

    return {
        "active_prints": active_prints,
        "active_frames": active_frames,
        "active_albums": active_albums,
        "total_cost": total_print_cost + total_frame_cost + total_album_cost,
    }
