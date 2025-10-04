from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Recipe
from .serializers import RecipeSerializer


class RecipeListView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class RecipeDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
