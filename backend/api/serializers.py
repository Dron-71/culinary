from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from recipes.models import AmountIngredientRecipe, Ingredient, Recipe, Tag
from users.models import Subscription

User = get_user_model()


class CurrentUserSerializer(ModelSerializer):
    """Отображение пользователя."""
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Отображение - подписан ли пользователь на автора."""
        request = self.context.get('request')
        return (request.user.is_authenticated
                and Subscription.objects.filter(
                    user=request.user, author=obj).exists())


class SubscriptionsGetSerializer(CurrentUserSerializer):
    """Отображание подписок."""
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscription.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                'Подписка уже оформлена.',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                'Нельзя подписываться на самого себя.',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes(self, obj):
        """Список рецептов текущего пользователя."""
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeSerializer(recipes, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        """Количество рецептов у текущего пользователя."""
        return obj.recipes.count()


class IngredientSerializer(ModelSerializer):
    """Отображение ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):
    """Отображение списока тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


class AmountIngredientRecipeSerializer(ModelSerializer):
    """Отображение ингридиентов в рецепте."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountIngredientRecipe
        fields = 'id', 'name', 'measurement_unit', 'amount'


class RecipeGetSerializer(ModelSerializer):
    """Отображение рецепта."""
    tags = TagSerializer(many=True)
    author = CurrentUserSerializer(read_only=True)
    ingredients = AmountIngredientRecipeSerializer(
        many=True,
        required=True,
        source='ingredients_in_recipe'
    )
    image = Base64ImageField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        """Отображение добавленых в избранное рецептов."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Отображение добавленых в корзину рецептов."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


class RecipeIngredientPostSerializer(ModelSerializer):
    """"Отображение ингредиентов при создании рецептов."""
    id = IntegerField(write_only=True)

    class Meta:
        model = AmountIngredientRecipe
        fields = 'id', 'amount'


def validate(self, value):
    if not value:
        raise ValidationError(
            {'ingredients':
             'Рецепт должен сосотоять минимум из 1 ингридиента.'}
        )
    for i in value:
        if i['amount'] <= 0:
            raise ValidationError(
                {'amount': 'Укажите правильное кол-во ингридиентов.'}
            )
    return value


class RecipePostSerializer(ModelSerializer):
    """Отображение рецепта при создании, изменении и удалении."""
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True)
    author = CurrentUserSerializer(read_only=True)
    ingredients = RecipeIngredientPostSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError(
                {'tags': 'В рецепте должен быть указан хотябы 1 тэг.'})
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError(
                {'ingredients':
                    'Рецепт должен сосотоять минимум из 1 ингридиента.'}
            )
        ingredients_list = []
        for items in ingredients:
            ingredient = get_object_or_404(Ingredient, id=items['id'])
            if ingredient in ingredients_list:
                raise ValidationError(
                    {'ingredients':
                        f'Ингредиент {ingredient} уже есть в рецепте.'}
                )
            ingredients_list.append(ingredient)
            if int(items['amount']) <= 0:
                raise ValidationError(
                    {'amount': 'Укажите правильное кол-во ингридиентов.'}
                )
        return ingredients

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise ValidationError({'errors': 'Укажите время больше нуля.'})
        return cooking_time

    @staticmethod
    def create_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            AmountIngredientRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        """Создает рецепт."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Изменение рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(
            recipe=instance, ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Представление рецепта."""
        request = self.context.get('request')
        context = {'request': request}
        return RecipeGetSerializer(instance, context=context).data


class RecipeSerializer(ModelSerializer):
    """Превью рецепта."""
    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
