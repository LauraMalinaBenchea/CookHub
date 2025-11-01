import os

from django.db.models import Avg
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Ingredient,
    Recipe,
    RecipePrivacyChoices,
    RecipeRating,
    Unit,
)
from .serializers import (
    IngredientAutocompleteSerializer,
    RecipeRatingSerializer,
    RecipeReadSerializer,
    RecipeSerializer,
    RecipeUploadSerializer,
    UnitSerializer,
)
from .utils.file_extraction import extract_text_from_file
from .utils.recipe_processing import parse_recipe_from_text
from .utils.recipe_recommendation import (
    filter_recipes_by_ingredients,
    get_recipes_based_on_users_with_similar_preferences,
    surprise_recipes,
)


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


class RecommendRecipesDBView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        ingredient_names = request.data.get("ingredients", [])
        my_recipes = request.data.get("my_recipes", False)
        num_choices = request.data.get("num_choices", None)
        title = request.data.get("title", "")
        creator = request.data.get("creator", "")

        current_user = request.user if request.user.is_authenticated else None

        if my_recipes:
            qs = Recipe.objects.filter(user=request.user)
        else:
            qs = Recipe.objects.filter(privacy=RecipePrivacyChoices.PUBLIC)

        if ingredient_names:
            qs = filter_recipes_by_ingredients(ingredient_names)
        if title:
            qs = qs.filter(title__icontains=title)
        if creator and not my_recipes:
            qs = qs.filter(created_by__username__icontains=creator)

        qs = qs.distinct()

        if num_choices is not None and current_user:
            qs = get_recipes_based_on_users_with_similar_preferences(
                qs, current_user
            )
            qs = surprise_recipes(qs, ingredient_names, num_choices)

        serializer = RecipeReadSerializer(qs, many=True)
        return Response(serializer.data)


class RecipeRatingCreateUpdateView(generics.GenericAPIView):
    serializer_class = RecipeRatingSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        recipe = Recipe.objects.get(pk=pk)

        rating_obj, created = RecipeRating.objects.get_or_create(
            user=request.user,
            recipe=recipe,
            defaults={"rating": request.data.get("rating")},
        )

        if not created:
            rating_obj.rating = request.data.get("rating")
            rating_obj.save()

        serializer = self.get_serializer(rating_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecipeRatingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            rating = RecipeRating.objects.get(user=request.user, recipe_id=pk)
            return Response({"rating": rating.rating})
        except RecipeRating.DoesNotExist:
            return Response({"rating": None})


class RecipeRatingAvgView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        ratings = RecipeRating.objects.filter(recipe_id=pk)
        avg = ratings.aggregate(Avg("rating"))["rating__avg"] or 0
        return Response({"avg_rating": avg})
