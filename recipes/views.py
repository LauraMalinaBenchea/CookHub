from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Ingredient, Recipe, RecipePrivacyChoices
from .serializers import IngredientAutocompleteSerializer, RecipeSerializer


class RecipeListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeSerializer

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublicRecipeListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.filter(privacy=RecipePrivacyChoices.PUBLIC)


class RecipeDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class IngredientAutocompleteView(generics.ListAPIView):
    serializer_class = IngredientAutocompleteSerializer

    def get_queryset(self):
        q = self.request.query_params.get("q", "")
        return Ingredient.objects.filter(name__icontains=q)[:5]
