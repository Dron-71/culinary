import csv

from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка данных из csv файла.'

    def handle(self, *args, **kwargs):
        with open('data/ingredients.csv', encoding='utf-8') as file:
            ingredient_file = csv.reader(file)
            for ingredients in ingredient_file:
                name, measurement_unit = ingredients
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                    )

        self.stdout.write('Ингридиенты загружены.')
