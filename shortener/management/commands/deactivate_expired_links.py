from django.core.management.base import BaseCommand
from shortener.models import Link

class Command(BaseCommand):

    help = "Deactivate all currently active links that have expired."

    def handle(self, *args, **options):
        for link in Link.objects.filter(is_active=True):
            link.deactivate_if_expired()
        return 0
