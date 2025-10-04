from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    servings = models.IntegerField(default=1)
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient"
    )

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    # Recipe-specific fields:
    quantity = models.FloatField()
    unit = models.CharField(max_length=50, blank=True)

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
