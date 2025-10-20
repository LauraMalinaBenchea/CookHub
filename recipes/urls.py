from django.urls import path

from .views import (
    IngredientAutocompleteView,
    PublicRecipeListView,
    RecipeDetailUpdateDeleteView,
    RecipeListView,
    RecipeUploadView,
)

urlpatterns = [
    path("recipe_list/", RecipeListView.as_view(), name="recipe_list"),
    path(
        "public_recipe_list/",
        PublicRecipeListView.as_view(),
        name="public_recipe_list",
    ),
    path(
        "recipe_detail/<int:pk>/",
        RecipeDetailUpdateDeleteView.as_view(),
        name="recipe_detail",
    ),
    path(
        "ingredients-autocomplete/",
        IngredientAutocompleteView.as_view(),
        name="ingredient-autocomplete",
    ),
    path("upload/", RecipeUploadView.as_view(), name="file_upload_recipe"),
]
