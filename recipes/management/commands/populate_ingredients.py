import openai
from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.management.constants import INGREDIENTS
from recipes.models import Ingredient

openai.api_key = settings.OPENAI_API_KEY


class Command(BaseCommand):
    help = "Populate a starter set of common ingredients"

    def handle(self, *args, **kwargs):
        for item in INGREDIENTS:
            Ingredient.objects.get_or_create(
                name=item["name"],
                defaults={
                    "nutritional_info": item.get("nutritional_info", {}),
                    "allergens": item.get("allergens", []),
                },
            )
        self.stdout.write(
            self.style.SUCCESS("Ingredients populated successfully.")
        )
