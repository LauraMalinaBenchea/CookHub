import os

from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeRating,
    Step,
    Unit,
    UploadedFile,
)
from recipes.utils.recipe_processing import convert_unit


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name"]


class IngredientAutocompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name"]


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    ingredient = serializers.CharField(source="ingredient.name")
    unit = serializers.CharField(source="unit.abbreviation")
    unit_id = serializers.IntegerField(source="unit.id")

    class Meta:
        model = RecipeIngredient
        fields = ["id", "ingredient", "quantity", "unit", "unit_id"]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = serializers.CharField(
        source="ingredient.name", read_only=True
    )
    ingredient_name = serializers.CharField(write_only=True)
    unit = serializers.CharField(source="unit.abbreviation", read_only=True)
    unit_id = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(), write_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = [
            "ingredient",
            "ingredient_name",
            "quantity",
            "unit",
            "unit_id",
        ]

    def create(self, validated_data):
        ingredient_name = validated_data.pop("ingredient_name")
        ingredient_obj, _ = Ingredient.objects.get_or_create(
            name=ingredient_name
        )

        unit_obj = validated_data.pop("unit_id")  # this is now a Unit instance
        return RecipeIngredient.objects.create(
            ingredient=ingredient_obj,
            unit=unit_obj,
            **validated_data,
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        system = self.context.get("system", "metric")
        from_unit = instance.unit
        if from_unit.system != system:
            quantity, new_unit = convert_unit(
                instance.quantity, from_unit, system
            )
            data["quantity"] = quantity
            data["unit"] = new_unit
        else:
            data["unit"] = from_unit.abbreviation
        return data


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ["id", "order", "text"]


class RecipeSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source="recipe_ingredients"
    )

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
        steps_data = validated_data.pop("steps")
        ingredients_data = validated_data.pop("recipe_ingredients")
        recipe = Recipe.objects.create(**validated_data)

        for ing_data in ingredients_data:
            ingredient_name = ing_data.pop("ingredient_name")
            ingredient_obj, _ = Ingredient.objects.get_or_create(
                name=ingredient_name
            )
            unit_obj = ing_data.pop("unit_id")

            ing_data.pop("unit", None)

            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_obj,
                unit=unit_obj,
                **ing_data,
            )
        for step_data in steps_data:
            Step.objects.create(recipe=recipe, **step_data)

        return recipe

    def update(self, instance, validated_data):
        steps_data = validated_data.pop("steps", [])
        ingredients_data = validated_data.pop("recipe_ingredients", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.recipe_ingredients.all().delete()
        for ing_data in ingredients_data:
            ingredient_name = ing_data.pop("ingredient_name")
            ingredient_obj, _ = Ingredient.objects.get_or_create(
                name=ingredient_name
            )
            unit_obj = ing_data.pop("unit_id")
            ing_data.pop("unit", None)
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient_obj,
                unit=unit_obj,
                **ing_data,
            )

        instance.steps.all().delete()
        for i, step_data in enumerate(steps_data):
            step_data.pop("order", None)
            Step.objects.create(recipe=instance, order=i + 1, **step_data)

        return instance

    def get_ingredients(self, obj):
        system = self.context.get("system", "metric")
        ingredients = []
        for ri in obj.recipe_ingredients.all():
            quantity = ri.quantity
            unit = ri.unit.abbreviation
            if ri.unit.system != system:
                quantity, unit = convert_unit(ri.quantity, ri.unit, system)
            ingredients.append(
                {
                    "id": ri.id,
                    "ingredient": ri.ingredient.name,
                    "quantity": quantity,
                    "unit": unit,
                }
            )
        return ingredients


class RecipeReadSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True, source="recipe_ingredients", read_only=True
    )

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


class RecipeUploadSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    file = serializers.FileField()

    class Meta:
        model = UploadedFile
        fields = ["name", "file"]

    def validate_file(self, file):
        allowed_extensions = [".pdf", ".docx"]
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError("Unsupported file extension.")
        max_size = 15 * 1024 * 1024  # 15 MB
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


class RecipeRatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = RecipeRating
        fields = ["id", "user", "recipe", "rating", "created_at"]
        read_only_fields = ["id", "user", "created_at", "recipe"]
