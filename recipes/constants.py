recipe_step_keywords = ["directions", "steps", "instructions", "method"]
recipe_ingredient_keywords = ["ingredients", "what you will need"]

UNIT_SYNONYMS = {
    "g": ["g", "gram", "grams", "gr"],
    "kg": ["kg", "kgs", "kilogram", "kilograms"],
    "ml": ["ml", "mililiter", "mililiters", "milliliter", "milliliters"],
    "l": ["l", "liter", "liters"],
    "oz": ["oz", "ounce", "ounces"],
    "lb": ["lb", "pound", "pounds"],
    "pcs": ["pcs", "piece", "pieces"],
    "tsp": ["tsp", "teaspoon", "teaspoons"],
    "tbsp": ["tbsp", "tablespoon", "tablespoons"],
    "cup": ["cup", "cups"],
}

UNIVERSAL_UNITS = ["pcs"]

CATEGORIES = {
    "g": "weight",
    "kg": "weight",
    "ml": "volume",
    "l": "volume",
    "tsp": "volume",
    "tbsp": "volume",
    "cup": "volume",
}
