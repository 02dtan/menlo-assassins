import csv
import random
import string

from decouple import config
from django.core.management.base import BaseCommand
from django.db import transaction
from tqdm import tqdm

from elimination.models import Senior


def get_initial_password():
    return ''.join(random.choices(string.ascii_uppercase, k=5))


class Command(BaseCommand):
    def handle(self, *args, **options):
        Senior.objects.all().delete()

        with open('students.csv', 'r') as students_file:
            with transaction.atomic():
                Senior.objects.create_superuser('admin', password=config('SUPERUSER_PASSWORD'),
                                                first_name='Super', last_name='User')
                students_csv = csv.reader(students_file, delimiter=',')
                next(students_csv)  # Skip CSV header
                seniors = tqdm(students_csv)
                for senior_csv in seniors:
                    email = senior_csv[1]
                    first_name = senior_csv[2].capitalize()
                    last_name = senior_csv[3].capitalize()
                    student_id = senior_csv[4].split('@')[0]
                    initial_password = get_initial_password()
                    # seniors.write(f"Creating {student_id}: {first_name} {last_name}: {initial_password}")
                    seniors.set_description(f"Creating {student_id}: {first_name} {last_name}: {initial_password}")
                    Senior.objects.create_user(student_id, email, initial_password,
                                               initial_password=initial_password,
                                               first_name=first_name, last_name=last_name)
