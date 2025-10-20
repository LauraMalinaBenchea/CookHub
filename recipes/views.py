import os

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Ingredient, Recipe, RecipePrivacyChoices
from .serializers import (
    IngredientAutocompleteSerializer,
    RecipeSerializer,
    RecipeUploadSerializer,
)
from .utils import extract_text_from_file, parse_recipe_from_text


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


class RecipeUploadView(generics.CreateAPIView):
    serializer_class = RecipeUploadSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data["file"]
        ext = os.path.splitext(uploaded_file.name)[1].lower()

        try:
            extracted_text = extract_text_from_file(uploaded_file, ext)
            recipe = parse_recipe_from_text(extracted_text, self.request.user)

            return Response(
                {
                    "message": "File processed and recipe created.",
                    "recipe": RecipeSerializer(recipe).data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
