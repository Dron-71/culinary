from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingList, Tag)
from rest_framework.fields import IntegerField
from rest_framework.serializers import (CharField, ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField, ValidationError)
from users.models import Subscription, User

from .fields import Base64ImageField


class IsUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed',)

    def get_is_subscribed(self, obj):
        """Подписан ли текущий пользователь на автора."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj.author).exists()


class CreateUserSerializer(UserCreateSerializer):
    """Профиль пользователя при регистрации."""
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')
        read_only_fields = 'id',

    def validate_username(self, value):
        if value.lower() == 'me':
            raise ValidationError(f'Логин {value} уже кем-то занят.')
        return value


class SubscribeSerializer(ModelSerializer):
    """Подписываемся и отписываемся от автора."""
    class Meta:
        model = Subscription
        fields = '__all__'

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        serializer = SubscriptionsSerializer(
            instance,
            context=context
        )
        return serializer.data

    def validate(self, data):
        user = data.get('user')
        author = data.get('author')
        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя.')
        if Subscription.objects.filter(user=user, author=author).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя.')
        return data


class SubscriptionsSerializer(CreateUserSerializer):
    """Отображение подписок."""
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)

    def get_recipes(self, obj):
        """Список рецептов текущего пользователя."""
        limit = self.context.get('request').GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj)
        if limit:
            queryset = queryset[:int(limit)]
        return RecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        """Количество рецептов у текущего пользователя."""
        return obj.recipes.count()


class TagSerializer(ModelSerializer):
    """Отображение списока тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    """Отображение ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'
        order_by = '-name',


class RecipeIngredientGetSerializer(ModelSerializer):
    """Отображение ингридиентов в рецепте."""
    id = ReadOnlyField(source='ingredient.id')
    name = CharField(source='ingredient.name')
    measurement_unit = CharField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = 'id', 'name', 'measurement_unit', 'amount',


class RecipeIngredientPostSerializer(ModelSerializer):
    """Отображение ингридиентов в рецепте."""
    id = IntegerField()
    amount = IntegerField(write_only=True)

    class Meta:
        model = IngredientRecipe
        fields = 'id', 'amount',


class RecipeSerializer(ModelSerializer):
    """Превью рецептов."""
    class Meta:
        model = Recipe
        fields = 'name', 'id', 'cooking_time', 'image',


class RecipeGetSerializer(ModelSerializer):
    """Отображение рецепта в избранном и корзине."""
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientGetSerializer(
        many=True, read_only=True, source='ingredients_in_recipe')
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'
        exclude = 'pub_date',

    def get_is_favorited(self, obj):
        """Находится ли в избранном."""
        request = self.context.get('request')
        return (request
                and request.user.is_authenticated
                and Favorite.objects.filter(
                    recipes=obj, like_recipes=request.user).exists())

    def get_is_in_shopping(self, obj):
        """Находится ли в корзине."""
        request = self.context.get('request')
        return (request
                and request.user.is_authenticated
                and ShoppingList.objects.filter(
                    recipes=obj, cart_owner=request.user).exists())


class RecipePostSerializer(ModelSerializer):
    """Отображение рецепта при создании, изменении и удалении."""
    author = UserSerializer(read_only=True)
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    ingredients = RecipeIngredientPostSerializer(many=True)
    cooking_time = IntegerField()
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = '__all__'

    def create_ingridients(self, ingredients, recipes):
        """Добавление ингридиентов в рецепт."""
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipes=recipes,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create_recipe(self, validated_data):
        """Создание рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipes = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredients(recipes=recipes, ingredients=ingredients)
        recipes.tags.set(tags)
        return recipes

    @transaction.atomic
    def update_recipe(self, instance, validated_data):
        """Изменение рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(recipes=instance, ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Представление рецепта."""
        return RecipeGetSerializer(instance, context=self.context).data


class FavoriteSerializer(ModelSerializer):
    """Отображение избранное."""
    class Meta:
        model = Favorite
        fields = 'user', 'recipes',

    def validate(self, obj):
        user = self.context['request'].user
        recipes = obj['recipes']
        favorite = user.favorites.filter(recipes=recipes).exists()

        if self.context.get('request').method == 'POST' and favorite:
            raise ValidationError('Этот рецепт уже добавлен в избранном')
        if self.context.get('request').method == 'DELETE' and not favorite:
            raise ValidationError('Этот рецепт отсутствует в избранном')
        return obj


class ShoppingListSerializer(ModelSerializer):
    """Отображение корзины."""
    class Meta:
        model = ShoppingList
        fields = '__all__'

    def validate(self, obj):
        user = self.context['request'].user
        recipes = obj['recipes']
        cart = user.cart.filter(recipes=recipes).exists()

        if self.context.get('request').method == 'POST' and cart:
            raise ValidationError('Рецепт уже добавлен в список покупок.')
        if self.context.get('request').method == 'DELETE' and not cart:
            raise ValidationError('Рецепт уже удален в списока покупок.')
        return obj

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data
