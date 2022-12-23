from django.db import models


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
    name = models.CharField('Tag_name', blank=False, max_length=200)
    color = models.CharField('Tag_color', max_length=7, blank=True)
    slug = models.SlugField('Tag_slug', max_length=200,
                            blank=True, unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name
