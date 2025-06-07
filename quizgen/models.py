import os

from django.db import models


class UploadedFile(models.Model):
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=10, blank=True)

    def save(self, *args, **kwargs):
        # Detect extension automatically
        self.file_type = self.set_file_type()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.file.name} ({self.file_type})"

    def set_file_type(self) -> str:
        ext = os.path.splitext(self.file.name)[1].lower()
        return ext.lstrip(".") if ext in [".pdf", ".docx"] else "unknown"
