from django.contrib.admin import ModelAdmin, TabularInline, register
from recipes.models import (
    FavoriteRecipe, Ingredient, IngredientAmount, Recipe, ShoppingCart, Tag)


@register(Tag)
class TagAdmin(ModelAdmin):
    """Настройка регистрация тэгов."""
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name', 'color')
    ordering = ('color',)
    empty_value_display = 'пусто'


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    """Настройки отображения таблицы с ингредиентами."""
    list_display = ('name', 'measurement_unit')
    ordering = ('name',)
    search_fields = ('name',)
    empty_value_display = 'пусто'


class IngredientAmountInline(TabularInline):
    model = IngredientAmount
    min_num = 1
    extra = 0


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    """Настройки отображения таблицы с рецептами."""
    list_display = ('name', 'author', 'count_favorites')
    list_filter = ['author', 'name', 'tags']
    inlines = (IngredientAmountInline,)

    def count_favorites(self, obj):
        return obj.favorites.count()

    count_favorites.short_description = "В избранном"


@register(FavoriteRecipe)
class FavoriteRecipeAdmin(ModelAdmin):
    """Настройки отображения таблицы с избранными рецептами."""
    list_display = ('pk', 'user', 'recipe')
    empty_value_display = 'пусто'


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    """Настройки отображения таблицы с корзиной покупок."""
    list_display = ('pk', 'user', 'recipe')
    empty_value_display = 'пусто'
