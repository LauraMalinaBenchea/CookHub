import logging
import re

import docx
import fitz
import nltk
import spacy
from django.db import transaction

from recipes.models import Ingredient, Recipe, RecipeIngredient, Step, Unit

nlp = spacy.load("en_core_web_sm")


nltk.download("punkt_tab")
logger = logging.getLogger(__name__)


def extract_text_from_file(file_obj: str, file_type: str) -> str:
    logger.info(f"Attempting to extract text from {file_type} file.")
    try:
        if file_type == ".pdf":
            return extract_text_from_pdf(file_obj)
        elif file_type == ".docx":
            return extract_text_from_docx(file_obj)
        else:
            logger.warning(f"Unsupported file type: {file_type}")
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as exc:
        logger.error(f"Error extracting text from file: {exc}")


def extract_text_from_pdf(file_obj: str) -> str:
    text = ""
    file_bytes = file_obj.read()
    with fitz.open(stream=file_bytes) as doc:

        for page in doc:
            text += page.get_text()
        logger.info(f"Extracted text from PDF with {len(doc)} pages.")

    file_obj.seek(0)
    return text


def extract_text_from_docx(file_obj: str) -> str:
    doc = docx.Document(file_obj)
    text = "\n".join([para.text for para in doc.paragraphs])
    logger.info(
        f"Extracted text from DOCX with {len(doc.paragraphs)} paragraphs."
    )
    file_obj.seek(0)
    return text


def parse_recipe_from_text(text: str, user, privacy="private") -> Recipe:
    """
    Parse raw text from a recipe file into a Recipe object and related models.
    """
    if not user:
        raise ValueError("User must be provided to create recipe.")

    # TODO: allow selecting privacy when uploading recipe
    # Normalize text
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    # joined = "\n".join(lines).lower()

    title = lines[0] if lines else "Untitled Recipe"

    ingredients_idx = None
    steps_idx = None

    for i, line in enumerate(lines):
        if re.search(r"ingredients?", line, re.I):
            ingredients_idx = i
        if re.search(r"(method|instructions|directions|steps)", line, re.I):
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

    ingredients_data = []
    ingredient_pattern = re.compile(
        r"(?P<quantity>\d+[\/\d\.]*)?\s*(?P<unit>[a-zA-Z]+)?\s*(?P<name>[a-zA-Z ,\-]+)"
    )

    for line in ingredient_lines:
        match = ingredient_pattern.match(line)
        if match:
            q = match.group("quantity")
            quantity = float(eval(q)) if q else 1.0
            unit = match.group("unit") or ""
            name = match.group("name").strip()
            ingredients_data.append((name, quantity, unit))

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

        for name, qty, unit in ingredients_data:
            ingredient, _ = Ingredient.objects.get_or_create(name=name.lower())
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                quantity=qty,
                unit=unit,
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
