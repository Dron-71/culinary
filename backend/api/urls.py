from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, SubscribeAPIView,
                    SubscribeListAPIView, TagViewSet)

app_name = 'api'

router = DefaultRouter()

router.register('users', SubscribeAPIView, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('users/subscriptions/', SubscribeListAPIView.as_view()),
    path('users/<int:user_id>/subscribe/', SubscribeAPIView.as_view()),
    path('', include(router.urls),),
    path('', include('djoser.urls'),),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
