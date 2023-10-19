from os import getenv
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

from users.models import User


load_dotenv()


class Command(BaseCommand):
    help = 'Создает базового суперпользователя, если он не существует.'
    requires_migrations_checks = True

    @staticmethod
    def create_custom_superuser(user_model):
        if not user_model.objects.filter(username='admin').exists():
            user_model.objects.create_superuser(
                email=getenv(
                    'SUPERUSER_EMAIL', '1@yandex.ru'
                ),
                username=getenv(
                    'SUPERUSER_USERNAME', 'Dron'
                ),
                first_name=getenv(
                    'SUPERUSER_FIRST_NAME', 'Андрей'
                ),
                last_name=getenv(
                    'SUPERUSER_LAST_NAME', 'Л'
                ),
                password=getenv(
                    'SUPERUSER_PASSWORD', 'admin'
                )
            )
            return True
        return False

    def handle(self, *args, **options):
        if self.create_custom_superuser(User):
            self.stdout.write(
                self.style.SUCCESS(
                    'Суперпользователь успешно создан'
                )
            )
        else:
            self.stdout.write(
                self.style.NOTICE(
                    'Суперпользователь уже существует'
                )
            )
