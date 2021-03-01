from django.core.management.base import BaseCommand
from django.db import transaction

from elimination.models import Senior


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('id_1', type=int)
        parser.add_argument('id_2', type=int)

    def handle(self, *args, **options):
        id_1 = options['id_1']
        id_2 = options['id_2']
        with transaction.atomic():
            senior_1 = Senior.objects.get(username=id_1)
            senior_2 = Senior.objects.get(username=id_2)
            senior_1.target = senior_2
            senior_2.target = senior_1
            senior_1.save()
            senior_2.save()
