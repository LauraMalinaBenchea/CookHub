from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_system = models.CharField(
        max_length=10,
        choices=[("metric", "Metric"), ("imperial", "Imperial")],
        default="metric",
    )
