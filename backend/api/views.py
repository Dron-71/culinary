from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .pagination import MainPagePagination
from .permissions import AuthorOrReadOnly
from .serializers import (CurrentUserSerializer, IngredientSerializer,
                          RecipeGetSerializer, RecipePostSerializer,
                          RecipeSerializer, SubscriptionsGetSerializer,
                          TagSerializer)

from recipes.models import (AmountIngredientRecipe, Favorite, Ingredient,
                            Recipe, ShoppingCart, Tag)
from users.models import Subscription


User = get_user_model()


class SubscribePost(UserViewSet):
    """Представление подписок пользователя."""
    queryset = User.objects.all()
    serializer_class = CurrentUserSerializer
    pagination_class = MainPagePagination

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        """Подписаться/отписаться от автора."""
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            serializer = SubscriptionsGetSerializer(
                author,
                data=request.data,
                context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = get_object_or_404(
            Subscription, user=user, author=author)
        subscription.delete()
        return Response(
            {'message': 'Отписались от автора'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Список подписок пользоваетеля."""
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsGetSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Представление игридиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(ReadOnlyModelViewSet):
    """Представление тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """ Представление рецепта."""
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = MainPagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Возвращает нужный сериализатор, в зависимости от запроса."""
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Добавление/удаление рецепта из избранное."""
        if request.method == 'POST':
            return self.add_recipe(Favorite, request.user, pk)
        return self.delete_recipe(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Добавление/удаление рецепта в корзину."""
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request.user, pk)
        return self.delete_recipe(ShoppingCart, request.user, pk)

    def add_recipe(self, model, user, pk):
        """Метод добавления объекта."""
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'errors': 'Объект уже есть в списке.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, user, pk):
        """Метод удаления объекта."""
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(
                {'detail': 'Объект успешно удален.'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'errors': 'Объект нет в списке.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачать рецепты."""
        ingredients = AmountIngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(amount=Sum('amount'))

        shopping_list = (
            f'Список покупок для: {request.user.get_full_name()}\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        response = FileResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping.txt"'
        return response
