from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Ingredient, Recipe
from .serializers import IngredientAutocompleteSerializer, RecipeSerializer


class RecipeListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class RecipeDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class IngredientAutocompleteView(generics.ListAPIView):
    serializer_class = IngredientAutocompleteSerializer

    def get_queryset(self):
        q = self.request.query_params.get("q", "")
        return Ingredient.objects.filter(name__icontains=q)[:5]
