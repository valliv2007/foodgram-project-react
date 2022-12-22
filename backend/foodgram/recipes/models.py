from django.db import models


class Ingredient(models.Model):
    """Модель ингридиентов"""
    name = models.CharField('Ingredient_name', blank=False, max_length=150)
    measurement_unit = models.CharField('Measurement_unit', max_length=150)

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name
