from django.db import models

from apps.core.models import BaseModel


class PrintJob(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PREPARING = "preparing", "Preparing"
        SENT = "sent", "Sent to Printer"
        PRINTING = "printing", "Printing"
        QC = "qc", "Quality Check"
        READY = "ready", "Ready"
        DELIVERED = "delivered", "Delivered"
        REPRINT = "reprint", "Reprint Required"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="print_jobs")
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="print_jobs")
    photo = models.ForeignKey(
        "gallery.Photo", on_delete=models.SET_NULL, null=True, blank=True, related_name="print_jobs"
    )
    print_size = models.CharField(max_length=50)
    quantity = models.IntegerField(default=1)
    paper_type = models.CharField(max_length=100, blank=True)
    vendor = models.CharField(max_length=200, blank=True)
    internal_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    customer_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    requested_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-requested_date"]

    def __str__(self):
        return f"Print {self.print_size} x{self.quantity} - {self.client}"

class FrameOrder(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ORDERED = "ordered", "Ordered"
        RECEIVED = "received", "Received"
        QC = "qc", "Quality Check"
        READY = "ready", "Ready"
        DELIVERED = "delivered", "Delivered"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="frame_orders")
    size = models.CharField(max_length=50)
    frame_type = models.CharField(max_length=100, blank=True)
    orientation = models.CharField(
        max_length=20,
        choices=[("portrait", "Portrait"), ("landscape", "Landscape")],
        default="portrait",
    )
    quantity = models.IntegerField(default=1)
    supplier = models.CharField(max_length=200, blank=True)
    internal_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    customer_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Frame {self.size} - {self.project.reference}"

class AlbumOrder(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending Selection"
        DESIGNING = "designing", "Designing"
        REVIEW = "review", "Internal Review"
        CLIENT_APPROVAL = "client_approval", "Client Approval"
        PRODUCTION = "production", "Sent For Production"
        RECEIVED = "received", "Received"
        QC = "qc", "Quality Check"
        DELIVERED = "delivered", "Delivered"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="album_orders")
    album_type = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=50, blank=True)
    pages = models.IntegerField(default=20)
    supplier = models.CharField(max_length=200, blank=True)
    design_status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    client_approved = models.BooleanField(default=False)
    cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    delivery_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Album {self.size} - {self.project.reference}"
