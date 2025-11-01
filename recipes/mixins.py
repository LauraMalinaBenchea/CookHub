from typing import Any

from django.db import models


class CreatedUpdatedAt(models.Model):
    """
    Abstract base class model that provides self-updating
    created_at and updated_at fields.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="Item created at.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="Item updated at.",
    )

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        update_fields = kwargs.get("update_fields", None)
        if update_fields:
            kwargs["update_fields"] = set(update_fields).union({"updated_at"})
        super().save(*args, **kwargs)

    def has_field_changed(self, field: str) -> bool:
        """
        Compares the field's in memory value with the one stored in the database. If
        they differ, it returns True, otherwise it returns False.
        If the field doesn't exist, AttributeError is raised.
        """
        try:
            return bool(
                self.pk
                and getattr(self, field)
                != getattr(self.__class__.objects.get(pk=self.pk), field)
            )
        except self.__class__.DoesNotExist:
            return False
