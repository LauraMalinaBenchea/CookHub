import random

from django.contrib.auth.models import User
from django.db.models import Count, Q, QuerySet

from recipes.models import Recipe, RecipeRating

"""
Recipe Recommendation Algorithm
Each function describes a single step in the recipe recommendation algorithm.

This combined approach produces recipe recommendations that are:
- Relevant (matching user-selected ingredients)
- Personalized (from users with similar tastes)
- Diverse (includes some new ingredients)
- Socially validated (average ratings considered)

Resources:
- https://en.wikipedia.org/wiki/Recommender_system#Content-based_filtering
- https://www.geeksforgeeks.org/machine-learning/recommendation-system-in-python/
"""


def filter_recipes_by_ingredients(ingredient_names: list[str]):
    """
     Step 1: Ingredient-based filtering:
    - Recipes are filtered to include at least one ingredient selected by the user.
    - Recipes are annotated with `matching_ingredients`
    (number of ingredients in common with the user’s selection).
    - Recipes are ordered by descending `matching_ingredients`
    to prioritize more relevant matches.
    """
    qs = (
        Recipe.objects.annotate(
            matching_ingredients=Count(
                "recipe_ingredients",
                filter=Q(
                    recipe_ingredients__ingredient__name__in=ingredient_names
                ),
            )
        )
        .filter(matching_ingredients__gt=0)
        .order_by("-matching_ingredients")
    )
    return qs


def get_recipes_based_on_users_with_similar_preferences(
    recipes_qs: QuerySet[Recipe],
    current_user: User,
) -> QuerySet[Recipe]:
    """
     Step 2: Collaborative filtering / user similarity:
    - Identify recipes the current user has already rated.
    - Find other users who have rated the same recipes.
    - Compute a similarity score for each user: increment when
    both users gave the same rating to the same recipe.
    - Select top N most similar users (e.g., 5) and collect
    recipes they rated highly that the current user hasn’t rated.
    - Merge these recipes with the ingredient-based queryset.
    """
    user_ratings = RecipeRating.objects.filter(user=current_user)
    user_rated_recipe_ids = set(
        user_ratings.values_list("recipe_id", flat=True)
    )

    other_ratings = RecipeRating.objects.exclude(user=current_user).filter(
        recipe_id__in=user_rated_recipe_ids
    )

    user_similarity = {}
    for r in other_ratings:
        match = any(
            ur.recipe_id == r.recipe_id and ur.rating == r.rating
            for ur in user_ratings
        )
        user_similarity[r.user_id] = user_similarity.get(r.user_id, 0) + (
            1 if match else 0
        )

    top_users = sorted(
        user_similarity.items(), key=lambda x: x[1], reverse=True
    )
    top_user_ids = [u for u, _ in top_users[:5]]

    similar_recipes = (
        RecipeRating.objects.filter(user_id__in=top_user_ids)
        .exclude(recipe_id__in=user_rated_recipe_ids)
        .values_list("recipe_id", flat=True)
    )

    ingredient_recipe_ids = list(recipes_qs.values_list("id", flat=True))
    similar_recipe_ids = list(similar_recipes)
    combined_ids = set(ingredient_recipe_ids) | set(similar_recipe_ids)

    qs = Recipe.objects.filter(id__in=combined_ids)
    return qs


def surprise_recipes(
    recipes: QuerySet,
    user_ingredients: list[str],
    num_choices: int = 3,
    alpha: int = 1,
    beta: int = 2,
) -> list[Recipe]:
    """
     Step 3: Diversity scoring (`surprise_recipes`):
    - For each recipe, compute:
        matching_count = ingredients overlapping with the user’s selection.
        new_ingredient_count = ingredients not already selected by the user.
    - Compute a weighted score: `
    score = alpha * matching_count + beta * new_ingredient_count`.
    - Use weighted random selection to pick final recipes,
    balancing familiarity and novelty.
    """
    scored_recipes = []
    for r in recipes:
        recipe_ingredients = set(
            i.ingredient.name for i in r.recipe_ingredients.all()
        )
        matching_count = len(recipe_ingredients & set(user_ingredients))
        new_ingredient_count = len(recipe_ingredients - set(user_ingredients))
        score = alpha * matching_count + beta * new_ingredient_count
        scored_recipes.append((r, score))

    # Weighted random choice
    total_score = sum(score for _, score in scored_recipes)
    if total_score == 0:
        # fallback to uniform random
        return random.sample(
            [r for r, _ in scored_recipes], min(num_choices, len(recipes))
        )

    weights = [score / total_score for _, score in scored_recipes]
    selected = random.choices(
        [r for r, _ in scored_recipes],
        weights=weights,
        k=min(num_choices, len(recipes)),
    )
    return selected
