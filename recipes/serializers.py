from rest_framework import serializers

from .models import Ingredient, Recipe, Step


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name", "quantity", "unit"]


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ["id", "text"]


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    steps = StepSerializer(many=True)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "title",
            "description",
            "servings",
            "ingredients",
            "steps",
        ]

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        steps_data = validated_data.pop("steps")

        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=recipe, **ingredient_data)

        for step_data in steps_data:
            Step.objects.create(recipe=recipe, **step_data)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        steps_data = validated_data.pop("steps")

        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get(
            "description", instance.description
        )
        instance.servings = validated_data.get("servings", instance.servings)
        instance.save()

        # Handle ingredients
        existing_ingredient_ids = [
            ing.id for ing in instance.ingredients.all()
        ]
        sent_ingredient_ids = [
            ing.get("id") for ing in ingredients_data if ing.get("id")
        ]

        # Delete removed ingredients
        for ing_id in existing_ingredient_ids:
            if ing_id not in sent_ingredient_ids:
                Ingredient.objects.filter(id=ing_id).delete()

        # Update or create ingredients
        for ing_data in ingredients_data:
            ing_id = ing_data.get("id", None)
            if ing_id:
                ing = Ingredient.objects.get(id=ing_id, recipe=instance)
                ing.name = ing_data.get("name", ing.name)
                ing.quantity = ing_data.get("quantity", ing.quantity)
                ing.unit = ing_data.get("unit", ing.unit)
                ing.save()
            else:
                Ingredient.objects.create(recipe=instance, **ing_data)

        # Handle steps
        existing_step_ids = [s.id for s in instance.steps.all()]
        sent_step_ids = [s.get("id") for s in steps_data if s.get("id")]

        for s_id in existing_step_ids:
            if s_id not in sent_step_ids:
                Step.objects.filter(id=s_id).delete()

        for step_data in steps_data:
            step_id = step_data.get("id", None)
            if step_id:
                step = Step.objects.get(id=step_id, recipe=instance)
                step.text = step_data.get("text", step.text)
                step.save()
            else:
                Step.objects.create(recipe=instance, **step_data)

        return instance
