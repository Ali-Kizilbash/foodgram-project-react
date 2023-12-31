import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open(f'{settings.BASE_DIR}/data/ingredients.json', 'r') as file:
            ingredients = json.loads(file.read())
            Ingredient.objects.bulk_create(
                Ingredient(**i) for i in ingredients)

        with open(f'{settings.BASE_DIR}/data/tags.json', 'r') as file:
            tags = json.loads(file.read())
            Tag.objects.bulk_create(
                Tag(**t) for t in tags)

        self.stdout.write('Ингредиенты и теги загружены')
