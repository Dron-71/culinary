from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    """Модель тэга"""
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        verbose_name='Название.',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Ед.изм.',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_ingredient')]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    name = models.CharField(
        verbose_name='Наименование.',
        max_length=200,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта.',
        on_delete=models.CASCADE,
        related_name='recipe',
    )
    image = models.ImageField(
        verbose_name='Картинка.',
        upload_to='media/recipe/images',
        blank=True,
        null=True,
    )
    text = models.TextField(
        verbose_name='Описание.',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список тегов.',
        related_name='recipe',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Список ингредиентов.',
        through='IngredientRecipe',
        related_name='ingredients',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах).',
        validators=[
            MinValueValidator(
                1, message='Укажите время больше нуля.'
            ),
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата создания.',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Ингридиенты в рецепта."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='В рецептах',
        related_name='ingredients_in_recipe',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Необходимые ингредиенты.',
        related_name='ingredients_in_recipe',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        verbose_name='Количество.',
        default=1,
        validators=(
            MinValueValidator(
                1, message='Рецепт должен сосотоять минимум из 1 ингридиента.',
            ),
        ),
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            )
        ]

    def __str__(self):
        return f'{self.amount} - {self.ingredient}'


class ShoppingList(models.Model):
    """Модель - список покупок."""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь.',
        on_delete=models.CASCADE,
        related_name='shopping',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт в корзине',
        on_delete=models.CASCADE,
        related_name='shopping',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping'
            )
        ]

    def __str__(self):
        return f'Список покупок пользователя {self.user}: {self.recipe}.'


class Favorite(models.Model):
    """Модель - избранное."""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь.',
        on_delete=models.CASCADE,
        related_name='favorite',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorite',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recip} в избранных у {self.user}.'
