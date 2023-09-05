from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingList, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from users.models import Subscription, User

from .pagination import MainPagePagination
from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeGetSerializer,
                          RecipePostSerializer, RecipeSerializer,
                          SubscribeSerializer, SubscriptionsSerializer,
                          TagSerializer)


class SubscribeAPIView(APIView):
    """Подписываемся и отписываемся от автора."""
    permission_classes = (IsAuthenticated, )
    pagination_class = MainPagePagination

    def post(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        data = {'author': author.id, 'user': user.id}
        serializer = SubscribeSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        subscription = get_object_or_404(
            Subscription, user=user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeListAPIView(ListAPIView):
    """Отображение подписок."""
    serializer_class = SubscriptionsSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление ингредиенов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, )
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """Представление рецептов"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorAdminOrReadOnly, )
    pagination_class = MainPagePagination
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        """Возвращает нужный сериализатор."""
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        """Пользователь является автором."""
        return serializer.save(author=self.request.user)

    def update_recipe(self, serializer):
        """Редактирование рецепта."""
        return serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = RecipePostSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def __base(self, request, model, id=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)

        if request.method == 'POST':
            object = model.objects.filter(user=user, recipe=recipe)
            if object.exists():
                return Response('Объект уже есть в списке.',
                                status=status.HTTP_400_BAD_REQUEST
                                )
            model.objects.create(user=user, recipe=recipe)
            serializer = RecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            object = model.objects.filter(user=user, recipe=recipe)
            if not object.exists():
                return Response('Объекта нет в списке.',
                                status=status.HTTP_400_BAD_REQUEST
                                )
            object.delete()
            return Response('Удаление выполнено',
                            status=status.HTTP_204_NO_CONTENT
                            )
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite'
    )
    def favorite(self, request, id=None):
        """Добавление и удаление рецепта в избранное."""
        return self.__base(request, model=Favorite, id=id)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping'
    )
    def shopping(self, request, id=None):
        """Добавление и удаление рецепта в корзину."""
        return self.__base(request, model=ShoppingList, id=id)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        """Скачать рецепты."""
        def create_shopping_list(ingredients):
            shopping_list = ['Список покупок:\n']
            for ingredient in ingredients:
                name = ingredient['ingredient__name']
                unit = ingredient['ingredient__measurement_unit']
                amount = ingredient['ingredient_amount']
                shopping_list.append(f'\n{name} - {amount}, {unit}')
            return shopping_list

        ingredients = IngredientRecipe.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))

        shopping_list = create_shopping_list(ingredients)

        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping.txt"'
        return response
