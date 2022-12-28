import django_filters

from recipes.models import Ingredient


class IngredientFilter(django_filters.FilterSet):
    """Фильтр для произведений"""

    name = django_filters.CharFilter(
        field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
