from django.core.management.base import BaseCommand

import send_email
from elimination.models import GameUpdate


class Command(BaseCommand):
    def handle(self, *args, **options):
        game_update = GameUpdate.objects.order_by("-created_at").first()
        send_email.send_game_update(game_update)
