from django import forms
from django.forms import inlineformset_factory

from .models import Recipe, RecipeIngredient, Unit


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["title", "privacy", "description", "servings"]


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["ingredient", "quantity", "unit"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["unit"].queryset = Unit.objects.all()


RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    extra=0,
    can_delete=True,
)
