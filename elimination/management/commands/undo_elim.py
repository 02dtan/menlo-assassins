from django.core.management.base import BaseCommand
from django.db import transaction

from elimination.models import Elimination


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('elimination_id', type=int)

    def handle(self, *args, **options):
        elimination_id = options['elimination_id']
        with transaction.atomic():
            elimination = Elimination.objects.get(id=elimination_id)
            eliminated_seniors_target = elimination.eliminator.target
            elimination.eliminator.target = elimination.target
            elimination.eliminator.save()
            elimination.target.target = eliminated_seniors_target
            elimination.target.save()
            elimination.delete()
