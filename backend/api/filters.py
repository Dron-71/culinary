from django_filters.rest_framework import FilterSet
from django.db import models
from django_filters import CharFilter, ModelMultipleChoiceFilter, BooleanFilter
from recipes.models import Recipes, Ingredient, Tag


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов."""
    name = CharFilter(method='filtering_by_name')

    def filtering_by_name(self, queryset, name, value):
        if not value:
            return queryset

        starts_with = queryset.filter(name__istartswith=value).annotate(
            qs_order=models.Value(0, models.IntegerField())
        )
        contains = (
            queryset.filter(name__icontains=value)
            .exclude(name__in=starts_with.values('name'))
            .annotate(qs_order=models.Value(1, models.IntegerField()))
        )

        return starts_with.union(contains).order_by('qs_order')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')

    class Meta:
        model = Recipes
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(carts__user=self.request.user)
        return queryset
