from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import (AmountIngredientRecipe, Favorite, Ingredient, Recipe,
                     ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Отображение в админ зоне тэгов."""
    list_display = ('name', 'color', 'slug',)
    empty_value_display = settings.EMPTY_VALUE


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Отображение в админ зоне ингридиетов."""
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = settings.EMPTY_VALUE


class ShowIngredientRecipeFormSet(BaseInlineFormSet):
    """Проверка наличия ингридиентов в рецепте."""

    def clean(self):
        super().clean()
        has_ingredient = False
        for form in self.forms:
            if not form.cleaned_data.get('DELETE'):
                has_ingredient = True
        if not has_ingredient:
            raise ValidationError(
                'В рецепте должен быть хотя бы один ингредиент')


class ShowIngredientRecipe(admin.TabularInline):
    model = AmountIngredientRecipe
    extra = 0
    min_num = 1
    formset = ShowIngredientRecipeFormSet


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Отображение в админ зоне рецептов."""
    list_display = ('name', 'author', 'amount_favorites')
    list_filter = ('author', 'tags')
    search_fields = ('author', 'name', 'tags')
    inlines = (ShowIngredientRecipe, )
    empty_value_display = settings.EMPTY_VALUE

    @admin.display(description='Отмечен как избранное.')
    def amount_favorites(self, obj):
        """Количество добавлений в избранное."""
        return obj.favorites.count()


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Отображение в админ зоне списка покупок."""
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = settings.EMPTY_VALUE


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Отображение в админ зоне избранное."""
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe',)
    empty_value_display = settings.EMPTY_VALUE
