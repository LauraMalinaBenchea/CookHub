import logging
import re
from decimal import Decimal

import nltk
import spacy
from django.db import transaction

from recipes.constants import recipe_ingredient_keywords, recipe_step_keywords
from recipes.models import Ingredient, Recipe, RecipeIngredient, Step, Unit

nlp = spacy.load("en_core_web_sm")


nltk.download("punkt_tab")
logger = logging.getLogger(__name__)


def merge_broken_ingredient_lines(lines):
    merged = []
    buffer = ""

    quantity_pattern = re.compile(r"^\s*\d")
    modifier_pattern = re.compile(
        r"^(crushed|optional|extra|to serve|"
        r"chopped|minced|sliced|diced|grated)\b",
        re.I,
    )
    ingredient_like_pattern = re.compile(
        r"(parsley|basil|cheese|spinach|peas|oil|flour|"
        r"salt|sugar|milk|chicken|beef|onion|garlic)",
        re.I,
    )

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue

        if quantity_pattern.match(clean_line):
            # new ingredient (starts with number)
            if buffer:
                merged.append(buffer.strip())
            buffer = clean_line
        elif modifier_pattern.match(clean_line):
            # continuation modifier
            buffer += " " + clean_line
        elif ingredient_like_pattern.search(
            clean_line
        ) and not buffer.endswith("optional"):
            # likely a new ingredient (even without number)
            if buffer:
                merged.append(buffer.strip())
            buffer = clean_line
        else:
            buffer += " " + clean_line

    if buffer:
        merged.append(buffer.strip())

    return merged


def parse_ingredient_lines(ingredient_lines):
    all_units = list(Unit.objects.all())
    units = {u.abbreviation.lower(): u for u in all_units}
    units.update({u.name.lower(): u for u in all_units})
    fallback_unit = Unit.objects.filter(abbreviation="pcs").first()
    # TODO: fix some broken units not being parsed correctly
    optional_keywords = [
        "optional",
        "extra",
        "extras",
        "toppings",
        "to serve",
        "as needed",
        "if desired",
    ]

    merged_lines = merge_broken_ingredient_lines(ingredient_lines)
    ingredients_data = []

    quantity_pattern = re.compile(r"^\d+([\/\.\d]*)?")
    number_word_pattern = re.compile(
        r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\b", re.I
    )

    # The optional mode is set to True when we
    # identify optional keywords on an independent line
    optional_mode = False

    for line in merged_lines:
        original_line = line
        lower_line = line.strip().lower()

        # Handle optional keywords and ensure they are
        # removed from the line (ingredient data)
        if lower_line.strip() in optional_keywords:
            optional_mode = True
            continue

        for keyword in optional_keywords:
            if keyword in lower_line:
                optional_mode = True
                lower_line = re.sub(rf"\b{keyword}\b", "", lower_line).strip()

        is_optional = optional_mode

        # --- Extract quantity ---
        match = quantity_pattern.match(lower_line)
        if match:
            q_str = match.group(0)
            try:
                quantity = float(eval(q_str))
            except Exception:
                quantity = 1.0
            lower_line = lower_line[len(q_str) :].strip()
        else:
            word_match = number_word_pattern.search(lower_line)
            if word_match:
                word_to_num = {
                    "one": 1,
                    "two": 2,
                    "three": 3,
                    "four": 4,
                    "five": 5,
                    "six": 6,
                    "seven": 7,
                    "eight": 8,
                    "nine": 9,
                    "ten": 10,
                }
                quantity = word_to_num[word_match.group(1).lower()]
                lower_line = lower_line.replace(
                    word_match.group(0), ""
                ).strip()
            else:
                quantity = 1.0

        # --- Detect unit ---
        unit = None
        for key, unit_obj in units.items():
            if re.search(rf"\b{re.escape(key)}\b", lower_line):
                unit = unit_obj
                lower_line = re.sub(
                    rf"\b{re.escape(key)}\b", "", lower_line
                ).strip()
                break
        if not unit:
            unit = fallback_unit

        name = lower_line.strip(" ,.-")

        ingredients_data.append(
            {
                "name": name,
                "quantity": Decimal(str(quantity)),
                "unit": unit,
                "is_optional": is_optional,
                "raw": original_line,
            }
        )

    return ingredients_data


def parse_recipe_from_text(text: str, user, privacy="private") -> Recipe:
    """
    Parse raw text from a recipe file into a Recipe object and related models.
    """
    if not user:
        raise ValueError("User must be provided to create recipe.")

    # TODO: allow selecting privacy when uploading recipe
    # Normalize text
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    title = lines[0] if lines else "Untitled Recipe"

    ingredients_idx = None
    steps_idx = None

    # TODO optimize understanding recipe data, to prevent
    #  fetching indexes based on recipe description
    ingredients_pattern = re.compile(
        r"|".join([re.escape(k) for k in recipe_ingredient_keywords]), re.I
    )
    steps_pattern = re.compile(
        r"|".join([re.escape(k) for k in recipe_step_keywords]), re.I
    )

    for i, line in enumerate(lines):
        if ingredients_pattern.search(line) and not ingredients_idx:
            ingredients_idx = i
        if steps_pattern.search(line) and not steps_idx:
            steps_idx = i

    if ingredients_idx is None:
        raise ValueError("No 'Ingredients' section found in text.")

    description_lines = []
    if ingredients_idx > 1:
        description_lines = lines[1:ingredients_idx]
    description = " ".join(description_lines)

    if steps_idx:
        ingredient_lines = lines[ingredients_idx + 1 : steps_idx]
        step_lines = lines[steps_idx + 1 :]
    else:
        ingredient_lines = lines[ingredients_idx + 1 :]
        step_lines = []

    ingredients_data = parse_ingredient_lines(ingredient_lines)
    print("Ingredients data", ingredients_data)

    steps = []
    for i, line in enumerate(step_lines):
        if re.match(r"^\d+[\).]", line):
            steps.append(line)
        elif steps:
            steps[-1] += " " + line
        else:
            steps.append(line)

    with transaction.atomic():
        recipe = Recipe.objects.create(
            title=title.strip(),
            description=description.strip(),
            privacy=privacy,
            servings=1,
            user=user,
        )

        for ing in ingredients_data:
            ingredient, _ = Ingredient.objects.get_or_create(
                name=ing["name"].lower()
            )
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                quantity=ing["quantity"],
                unit=ing["unit"],
                is_optional=ing["is_optional"],
            )

        for idx, step_text in enumerate(steps, start=1):
            Step.objects.create(recipe=recipe, order=idx, text=step_text)

    return recipe


def convert_unit(quantity, from_unit, to_system):
    """
    Convert a quantity from one unit to another system (metric/imperial).
    Returns: (converted_quantity, target_unit_abbreviation)
    """
    # Exclude category "count"
    if from_unit.category not in ["weight", "volume"]:
        return quantity, from_unit.abbreviation

    # Get all units in the same category
    category_units = Unit.objects.filter(category=from_unit.category)

    # Find the target system base
    to_units = category_units.filter(system=to_system)
    if not to_units.exists():
        return quantity, from_unit.abbreviation

    # Try to find a "base" target unit, or fallback to the first
    to_unit = to_units.filter(is_base_unit=True).first() or to_units.first()
    base_quantity = quantity * from_unit.base_conversion_factor
    converted_quantity = base_quantity / to_unit.base_conversion_factor

    # Round neatly: 0 decimals if whole number, else 1 decimal
    converted_quantity = (
        round(converted_quantity, 1)
        if converted_quantity % 1
        else int(converted_quantity)
    )

    return converted_quantity, to_unit.abbreviation
