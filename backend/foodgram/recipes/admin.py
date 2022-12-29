from django.contrib import admin

from .models import (Cart, Favorite, Ingredient, IngredientRecipe,
                     Recipe, Tag, TagRecipe)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    extra = 2


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name',)
    list_display = ('name', 'measurement_unit')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('name', 'author', 'tags')
    list_display = ('name', 'author')
    inlines = (IngredientRecipeInline, TagRecipeInline)
    fieldsets = (
        ('Main params', {'fields': (
            'name', 'author', 'image', 'text', 'cooking_time')}),
        ('Added to favorite', {'fields': ('favorite_count',)})
        )
    readonly_fields = ('favorite_count',)

    def favorite_count(self, obj):
        return obj.favorites.count()


admin.site.register(Tag)
admin.site.register(IngredientRecipe)
admin.site.register(TagRecipe)
admin.site.register(Cart)
admin.site.register(Favorite)
