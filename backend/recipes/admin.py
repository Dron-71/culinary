from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingList, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Отображение в админ зоне тэгов."""
    list_display = ('id', 'name', 'color', 'slug',)
    search_fields = ('name', 'color', 'slug')
    ordering = ('color',)
    empty_value_display = ('--пусто--')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Отображение в админ зоне ингридиетов."""
    list_display = ('id', 'name', 'measurement_unit')
    ordering = ('name',)
    search_fields = ('name',)
    empty_value_display = ('--пусто--')


class IngredientRecipelist(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1
    extra = 2


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Отображение в админ зоне рецептов."""
    list_display = ('id', 'name', 'author', 'amount_favorites')
    list_filter = ['author', 'name', 'tags']

    def amount_favorites(self, obj):
        return obj.favorites.count()


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Отображение в админ зоне списка покупок."""
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = ('--пусто--')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Отображение в админ зоне избранное."""
    list_display = ('id', 'user', 'recipe')
    empty_value_display = ('--пусто--')
