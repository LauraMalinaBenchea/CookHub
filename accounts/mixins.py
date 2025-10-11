from django.conf import settings
from django.db import models


class UserFK(models.Model):
    """
    Abstract base class model that provides a single field
    which links to the user model via a foreign key.
    """

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="%(class)ss",
        on_delete=models.CASCADE,
        verbose_name=("User"),
        help_text=("User linked to object."),
    )

    class Meta:
        abstract = True
