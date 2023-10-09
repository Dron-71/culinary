from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов."""
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_filter(self, queryset, value, filter_parameters):
        if self.request.user.is_authenticated and value:
            return queryset.filter(**filter_parameters)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        filter_parameters = {'favorites__user': self.request.user}
        return self.get_filter(queryset, value, filter_parameters)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        filter_parameters = {'shopping_cart__user': self.request.user}
        return self.get_filter(queryset, value, filter_parameters)
