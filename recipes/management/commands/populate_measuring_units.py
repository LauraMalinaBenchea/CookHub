from django.core.management.base import BaseCommand

from recipes.models import Unit


class Command(BaseCommand):
    help = "Populate Units table with default cooking measurement units"

    UNITS = [
        {
            "name": "gram",
            "abbreviation": "g",
            "category": "weight",
            "system": "metric",
            "base_conversion_factor": 1.0,
            "is_base_unit": True,
        },
        {
            "name": "kilogram",
            "abbreviation": "kg",
            "category": "weight",
            "system": "metric",
            "base_conversion_factor": 1000.0,
        },
        {
            "name": "ounce",
            "abbreviation": "oz",
            "category": "weight",
            "system": "imperial",
            "base_conversion_factor": 28.3495,
        },
        {
            "name": "pound",
            "abbreviation": "lb",
            "category": "weight",
            "system": "imperial",
            "base_conversion_factor": 453.592,
        },
        {
            "name": "milliliter",
            "abbreviation": "ml",
            "category": "volume",
            "system": "metric",
            "base_conversion_factor": 1.0,
            "is_base_unit": True,
        },
        {
            "name": "liter",
            "abbreviation": "l",
            "category": "volume",
            "system": "metric",
            "base_conversion_factor": 1000.0,
        },
        {
            "name": "cup",
            "abbreviation": "cup",
            "category": "volume",
            "system": "imperial",
            "base_conversion_factor": 240.0,
        },
        {
            "name": "tablespoon",
            "abbreviation": "tbsp",
            "category": "volume",
            "system": "imperial",
            "base_conversion_factor": 14.7868,
        },
        {
            "name": "teaspoon",
            "abbreviation": "tsp",
            "category": "volume",
            "system": "imperial",
            "base_conversion_factor": 4.92892,
        },
        {
            "name": "piece",
            "abbreviation": "pcs",
            "category": "count",
            "system": "metric",
            "base_conversion_factor": 1.0,
            "is_base_unit": True,
        },
        {
            "name": "piece",
            "abbreviation": "pcs",
            "category": "count",
            "system": "imperial",
            "base_conversion_factor": 1.0,
            "is_base_unit": True,
        },
    ]

    def handle(self, *args, **options):
        for u in self.UNITS:
            Unit.objects.update_or_create(
                name=u["name"],
                defaults=u,
            )
        self.stdout.write(self.style.SUCCESS("Units populated successfully."))
