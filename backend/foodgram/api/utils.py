from django.shortcuts import get_object_or_404

from recipes.models import Ingredient, IngredientRecipe, Tag, TagRecipe


def create_tags_and_ingredient_recipe(tags, ingredients, recipe):
    """Метод для создания объектов моделей TagRecipe и IngredientRecipe"""
    TagRecipe.objects.bulk_create(
            [TagRecipe(tag=get_object_or_404(Tag, id=tag),
             recipe=recipe) for tag in tags])
    IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']) for ingredient in ingredients])
