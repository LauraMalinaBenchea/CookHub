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
        # Should never be unknown because during form validation
        # an error would be raised
        return ext.lstrip(".") if ext in [".pdf", ".docx"] else "unknown"


class Quizz(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return self.title


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    quizz = models.ForeignKey(
        Quizz, on_delete=models.CASCADE, related_name="questions"
    )

    class Meta:
        ordering = ["question_text"]

    def __str__(self):
        return self.question_text


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    answer_text = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["answer_text"]

    def __str__(self):
        return self.answer_text
