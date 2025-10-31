import os

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Ingredient, Recipe, RecipePrivacyChoices, Unit
from .serializers import (
    IngredientAutocompleteSerializer,
    RecipeReadSerializer,
    RecipeSerializer,
    RecipeUploadSerializer,
    UnitSerializer,
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
    serializer_class = RecipeReadSerializer
    queryset = Recipe.objects.filter(privacy=RecipePrivacyChoices.PUBLIC)


class RecipeDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeReadSerializer
        return RecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["system"] = self.request.query_params.get("system", "metric")
        return context


class RecipeDetailReadOnlyView(generics.RetrieveAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["system"] = self.request.query_params.get("system", "metric")
        return context


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
            print("Extracted Text:\n", extracted_text[:1000])
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


class UnitListView(generics.ListAPIView):
    serializer_class = UnitSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        system = self.request.query_params.get("system")

        if not system and hasattr(self.request.user, "userprofile"):
            system = self.request.user.userprofile.preferred_system
        system = system or "metric"

        return Unit.objects.filter(system=system)
