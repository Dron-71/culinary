from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from pytils.translit import slugify
from users.models import User


class Tag(models.Model):
    """Модель таблицы тэга."""
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        unique=True,
    )
    color = ColorField(
        verbose_name='Цвет тега',
        format='hex',
        default='#FF0000',
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['-id']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:200]
        super().save(*args, **kwargs)


class Ingredient(models.Model):
    """Модель таблицы ингредиента."""
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
        db_index=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Ед.изм.',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель таблицы рецепта."""
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientAmount',
        related_name='ingredients',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes',
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to="static/recipe/",
        blank=True,
        null=True,
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (мин.)',
        validators=[
            MinValueValidator(
                1, 'Время приготовления не может быть меньше 1 минуты!'
            ),
        ],
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецеата',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата создания рецепта',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_recipe_name_author',
            )
        ]

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """Модель таблицы количества ингредиента."""
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Необходимые ингредиенты',
        on_delete=models.CASCADE,
        related_name='amount_ingredient',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='В рецептах',
        on_delete=models.CASCADE,
        related_name='amount_ingredient',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=1,
        validators=(
            MinValueValidator(
                1, message='Мин. количество ингридиентов 1'),),
    )

    class Meta:
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient',
            )
        ]

    def __str__(self):
        return f'{self.amount} - {self.ingredient}'


class FavoriteRecipe(models.Model):
    """Модель таблицы избранных рецептов."""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранный рецепт',
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления в избранные',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorites'
            )
        ]

    def __str__(self):
        return f'Любимый рецепт {self.recipe} пользователя {self.user}'


class ShoppingCart(models.Model):
    """Модель таблицы корзины покупок."""
    user = models.ForeignKey(
        User,
        verbose_name='Владелец покупок',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепты в списке покупок',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления в корзину',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='Рецепт уже добавлен в список покупок'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в корзину рецепт {self.recipe}'
