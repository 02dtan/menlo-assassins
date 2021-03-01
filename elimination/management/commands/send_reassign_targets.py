from django.core.management.base import BaseCommand

import send_email


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_email.send_reassign_targets()
