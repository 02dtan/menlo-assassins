from django.core.management.base import BaseCommand

from send_email import send_winners


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_winners()
