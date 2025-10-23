import os

from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Step,
    Unit,
    UploadedFile,
)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name"]


class IngredientAutocompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name"]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = serializers.CharField()  # <-- allow any string

    class Meta:
        model = RecipeIngredient
        fields = ["ingredient", "quantity", "unit"]

    def create(self, validated_data):
        ingredient_name = validated_data.pop("ingredient")
        ingredient_obj, _ = Ingredient.objects.get_or_create(
            name=ingredient_name
        )
        return RecipeIngredient.objects.create(
            ingredient=ingredient_obj, **validated_data
        )


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ["id", "order", "text"]


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True, source="recipe_ingredients"
    )
    steps = StepSerializer(many=True)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "title",
            "privacy",
            "description",
            "servings",
            "ingredients",
            "steps",
        ]

    def create(self, validated_data):
        """
        Create a recipe based on data populated in the form.
        Also handles the creation of related steps and ingredients if needed.
        """
        ingredients_data = validated_data.pop("recipe_ingredients")
        steps_data = validated_data.pop("steps")

        recipe = Recipe.objects.create(**validated_data)

        for ing_data in ingredients_data:
            ingredient_name = ing_data.pop("ingredient")
            ingredient_obj, _ = Ingredient.objects.get_or_create(
                name=ingredient_name
            )
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient_obj, **ing_data
            )

        for step_data in steps_data:
            Step.objects.create(recipe=recipe, **step_data)

        return recipe


class RecipeUploadSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    file = serializers.FileField()

    class Meta:
        model = UploadedFile
        fields = ["name", "file"]
        # try:
        #     extracted_text = extract_text_from_file(file_path, file_type)
        # except Exception as e:
        #     print(f"Error extracting text: {e}")

    def validate_file(self, file):
        print("In validate file")
        allowed_extensions = [".pdf", ".docx"]
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError("Unsupported file extension.")
        max_size = 15 * 1024 * 1024  # 5 MB
        if file.size > max_size:
            raise serializers.ValidationError(
                "File too large. Max size is 15MB."
            )
        return file

    def validate(self, attrs):
        return attrs


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ["id", "name", "abbreviation", "category"]
