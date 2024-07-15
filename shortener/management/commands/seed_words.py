from django.core.management.base import BaseCommand
from shortener.models import Adjective, Noun
from shortener.config.database_seed import ADJECTIVES, NOUNS

class Command(BaseCommand):

    help = ("Add default adjectives and nouns to the respective database "
       "tables.")

    def handle(self, *args, **options):
        Adjective.objects.bulk_create(
            [Adjective(word=word) for word in ADJECTIVES],
            ignore_conflicts=True,
            unique_fields=['word']
        )
        Noun.objects.bulk_create(
            [Adjective(word=word) for word in NOUNS],
            ignore_conflicts=True,
            unique_fields=['word']
        )
        return 0
