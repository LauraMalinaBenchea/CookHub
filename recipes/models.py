import os

from django.db import models
from django.db.models import TextChoices

from accounts.mixins import UserFK


class RecipePrivacyChoices(TextChoices):
    PRIVATE = "private", "Only I can see this"
    PUBLIC = "public", "Anyone can see this"


class Unit(models.Model):
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)
    category = models.CharField(
        max_length=20,
        choices=[
            ("weight", "Weight"),
            ("volume", "Volume"),
            ("count", "Count"),
        ],
    )
    base_conversion_factor = models.FloatField(default=1.0)

    def __str__(self):
        return self.abbreviation


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Recipe(UserFK, models.Model):
    title = models.CharField(max_length=200)
    privacy = models.CharField(
        max_length=50,
        choices=RecipePrivacyChoices.choices,
        default=RecipePrivacyChoices.PRIVATE,
    )
    description = models.TextField(blank=True)
    servings = models.IntegerField(default=1)
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
    )

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipe_ingredients"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    quantity = models.FloatField()
    unit = models.ForeignKey(to=Unit, on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"{self.quantity} {self.unit} {self.ingredient.name} "
            f"(for {self.recipe.title})"
        )


class Step(models.Model):
    recipe = models.ForeignKey(
        Recipe, related_name="steps", on_delete=models.CASCADE
    )
    order = models.IntegerField()
    text = models.TextField()

    def __str__(self):
        return f"Step {self.order} for {self.recipe.title}"


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
        ext = os.path.splitext(self.file.name)[1].lower().lstrip(".")
        return ext if ext in ["pdf", "docx"] else "unknown"
