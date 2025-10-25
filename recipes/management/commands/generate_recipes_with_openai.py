import json
import os
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from openai import OpenAI, OpenAIError

from recipes.models import Ingredient, Recipe, RecipeIngredient, Step, Unit


class Command(BaseCommand):
    help = (
        "Generate demo public recipes using OpenAI or "
        "fallback to local random recipes"
    )

    NUMBER_OF_RECIPES = 10

    SAMPLE_INGREDIENTS = [
        "flour",
        "sugar",
        "butter",
        "eggs",
        "milk",
        "salt",
        "baking powder",
        "chocolate",
        "vanilla",
        "tomato",
        "onion",
        "garlic",
        "olive oil",
        "cheese",
        "chicken",
        "beef",
        "carrot",
        "potato",
        "bell pepper",
        "rice",
        "pasta",
    ]

    SAMPLE_UNITS = ["g", "kg", "ml", "l", "tbsp", "tsp", "pcs"]

    SAMPLE_STEPS = [
        "Mix all ingredients together.",
        "Preheat the oven to 180°C.",
        "Cook until golden brown.",
        "Serve and enjoy!",
        "Chop the vegetables finely.",
        "Simmer for 20 minutes.",
        "Whisk the eggs until fluffy.",
    ]

    def handle(self, *args, **kwargs):
        author, _ = User.objects.get_or_create(username="demo_user")

        # Try OpenAI first
        api_key = os.getenv("OPENAI_API_KEY")
        recipes_data = None

        if api_key:
            try:
                client = OpenAI(api_key=api_key)
                prompt = f"""
                Generate {self.NUMBER_OF_RECIPES} recipes in JSON format.
                Each recipe should have:
                - title
                - description
                - servings (integer)
                - ingredients: array of objects with "name", "quantity", "unit"
                - steps: array of step texts
                Return only JSON.
                """
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                )
                recipes_data = json.loads(response.choices[0].message.content)
            except OpenAIError as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"OpenAI generation failed ({type(e).__name__}): {e}. "
                        f"Falling back to local recipes."
                    )
                )
            except json.JSONDecodeError:
                self.stdout.write(
                    self.style.WARNING(
                        "Failed to parse OpenAI response. "
                        "Falling back to local recipes."
                    )
                )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "OPENAI_API_KEY not set. Using local random recipes."
                )
            )

        # Fallback to random recipes if OpenAI failed
        if not recipes_data:
            recipes_data = []
            for i in range(self.NUMBER_OF_RECIPES):
                title = f"Demo Recipe {i+1}"
                servings = random.randint(1, 6)
                ingredients = []
                for _ in range(random.randint(3, 6)):
                    name = random.choice(self.SAMPLE_INGREDIENTS)
                    quantity = round(random.uniform(1, 500), 1)
                    unit = random.choice(self.SAMPLE_UNITS)
                    ingredients.append(
                        {"name": name, "quantity": quantity, "unit": unit}
                    )
                steps = random.sample(
                    self.SAMPLE_STEPS, k=random.randint(2, 5)
                )
                recipes_data.append(
                    {
                        "title": title,
                        "description": f"A tasty {title.lower()}",
                        "servings": servings,
                        "ingredients": ingredients,
                        "steps": steps,
                    }
                )

        # Save recipes to DB
        for r in recipes_data:
            recipe, _ = Recipe.objects.get_or_create(
                title=r["title"],
                defaults={
                    "description": r.get("description", ""),
                    "servings": r.get("servings", 1),
                    "privacy": "public",
                    "user": author,
                },
            )

            for ing in r.get("ingredients", []):
                ingredient_obj, created = Ingredient.objects.get_or_create(
                    name__iexact=ing["name"], defaults={"name": ing["name"]}
                )
                unit_obj, _ = Unit.objects.get_or_create(
                    abbreviation__iexact=ing["unit"]
                )
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient_obj,
                    quantity=ing["quantity"],
                    unit=unit_obj,
                )

            for idx, step_text in enumerate(r.get("steps", []), 1):
                Step.objects.create(recipe=recipe, order=idx, text=step_text)

        self.stdout.write(
            self.style.SUCCESS(
                f"{self.NUMBER_OF_RECIPES} demo recipes generated successfully."
            )
        )
