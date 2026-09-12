from django.db import models

from apps.core.models import BaseModel


class Gallery(BaseModel):
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="galleries")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_selection = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.project.reference} - {self.name}"

class Photo(BaseModel):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name="photos")
    file_name = models.CharField(max_length=500)
    original_file_name = models.CharField(max_length=500, blank=True)
    storage_key = models.CharField(max_length=1000)
    thumbnail_key = models.CharField(max_length=1000, blank=True)
    preview_key = models.CharField(max_length=1000, blank=True)
    image_number = models.IntegerField(default=0)
    capture_date = models.DateTimeField(null=True, blank=True)
    is_selected = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["image_number"]

    def __str__(self):
        return f"{self.gallery.name} - #{self.image_number}"

class PhotoSelection(BaseModel):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name="selections")
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="photo_selections")
    is_favourite = models.BooleanField(default=False)
    finalized = models.BooleanField(default=False)

    class Meta:
        unique_together = [("photo", "client")]
