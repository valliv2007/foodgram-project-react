from django.contrib import admin

from .models import Ingredient, IngredientRecipe, Recipe, Tag, TagRecipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name',)
    list_display = ('name', 'measurement_unit')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('name', 'author', 'tags')
    list_display = ('name', 'author')


admin.site.register(Tag)
admin.site.register(IngredientRecipe)
admin.site.register(TagRecipe)
