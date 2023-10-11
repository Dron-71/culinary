from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UA

from .models import Subscription, User


@admin.register(User)
class UserAdmin(UA):
    """Отображение в админ зоне пользователя."""
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('email', 'first_name',)
    empty_value_display = settings.EMPTY_VALUE


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    """Отображение в админ зоне подписчиков."""
    list_display = ('user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    empty_value_display = settings.EMPTY_VALUE
