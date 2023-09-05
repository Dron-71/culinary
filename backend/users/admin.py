from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Отображение в админ зоне пользователя."""
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_editable = ('username', 'email', 'first_name', 'last_name')
    empty_value_display = ('--пусто--')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    empty_value_display = ('--пусто--')
