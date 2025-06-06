import os

from django.db import models


class UploadedFile(models.Model):
    FILE_TYPES = [
        ("pdf", "PDF"),
        ("docx", "DOCX"),
    ]

    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(
        max_length=10, choices=FILE_TYPES, editable=False
    )

    def save(self, *args, **kwargs):
        # Detect extension automatically
        ext = os.path.splitext(self.file.name)[1].lower()
        if ext == ".pdf":
            self.file_type = "pdf"
        elif ext == ".docx":
            self.file_type = "docx"
        else:
            self.file_type = "unknown"  # fallback if we ever expand
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.file.name} ({self.file_type})"
