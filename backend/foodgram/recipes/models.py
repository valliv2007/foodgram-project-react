from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

MINIMAL_VALUE = 1


class Ingredient(models.Model):
    """Модель ингридиентов"""
    name = models.CharField('Ingredient_name', blank=False, max_length=200)
    measurement_unit = models.CharField('Measurement_unit', max_length=200)

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тегов"""
    name = models.CharField(
        'Tag_name', blank=False, max_length=200, unique=True)
    color = models.CharField(
        'Tag_color', max_length=7, blank=True, unique=True)
    slug = models.SlugField(
        'Tag_slug', max_length=200, blank=True, unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов"""
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe')
    tags = models.ManyToManyField(Tag, through='TagRecipe')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Recipe_author')
    name = models.CharField('Recipe_name', blank=False, max_length=200)
    image = models.ImageField(
        'Recipe_image', upload_to='recipes/', blank=False)
    text = models.TextField('Recipe_text', blank=False)
    cooking_time = models.IntegerField(
        'Cooking_time', blank=False,
        validators=(MinValueValidator(
            MINIMAL_VALUE,
            f'Время приготовления должно быть не меньше {MINIMAL_VALUE}'
            ' минуты'),),)

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Модель связи ингридиентов и рецептов"""
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipes')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='ingredientrecipes')
    amount = models.IntegerField(
        'Amount', blank=False, validators=(MinValueValidator(
            MINIMAL_VALUE,
            f'Количество должно быть не менее {MINIMAL_VALUE}'),))

    class Meta:
        verbose_name = 'Ingredient_Recipe'
        verbose_name_plural = 'Ingredients_Recipes'

    def __str__(self):
        return (f'{self.recipe.name} included {self.amount} of'
                f' {self.ingredient.name}')


class TagRecipe(models.Model):
    """Модель связи тэгов и рецептов"""
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Tag_Recipe'
        verbose_name_plural = 'Tags_Recipes'

    def __str__(self):
        return (f'{self.recipe.name} has tag {self.tag.name}')


class Favorite(models.Model):
    """Модель избранного"""
    user = models.ForeignKey(User,
                             related_name="favorites",
                             on_delete=models.CASCADE,
                             verbose_name="Favorite_user")
    recipe = models.ForeignKey(Recipe,
                               related_name="favorites",
                               on_delete=models.CASCADE,
                               verbose_name="Favorite_recipe")

    def __str__(self):
        return f'{self.user} add to favorite {self.recipe}'

    class Meta:
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                       name='unique_favorite')]


class Cart(models.Model):
    """Модель списка покупок"""
    user = models.ForeignKey(User,
                             related_name="carts",
                             on_delete=models.CASCADE,
                             verbose_name="Cart_user")
    recipe = models.ForeignKey(Recipe,
                               related_name="carts",
                               on_delete=models.CASCADE,
                               verbose_name="Cart_recipe")

    def __str__(self):
        return f'{self.user} add to cart {self.recipe}'

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                       name='unique_cart')]
