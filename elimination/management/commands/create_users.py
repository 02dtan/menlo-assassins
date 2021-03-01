import random
import re

from decouple import config
from django.core.management.base import BaseCommand
from django.db import transaction
from tqdm import tqdm

from elimination.models import Senior


def get_initial_password():
    password = ""
    for i in range(0, 5):
        password += chr(random.randint(ord('A'), ord('Z')))
    return password


class Command(BaseCommand):
    def handle(self, *args, **options):
        Senior.objects.all().delete()

        seniors_file = open('seniors.csv', 'r').read()
        seniors_csv = re.split('\n', seniors_file)

        initial_passwords_file = open('initial_passwords.csv', 'w')

        with transaction.atomic():
            Senior.objects.create_superuser('admin', password=config('SUPERUSER_PASSWORD'),
                                            first_name='Super', last_name='User')
            seniors = tqdm(seniors_csv[1:])
            for senior_csv in seniors:
                line_csv = re.split(',', senior_csv)
                email = line_csv[1]
                full_name = line_csv[2]
                student_id = line_csv[3]
                initial_password = get_initial_password()
                name_list = re.split(" ", full_name)
                first_name = name_list[0].capitalize()
                last_name = name_list[1].capitalize()
                initial_passwords_file.write(f'{student_id}, {initial_password}\n')
                seniors.set_description(f"Creating {student_id}: {first_name} {last_name}")
                Senior.objects.create_user(student_id, email, initial_password,
                                           initial_password=initial_password,
                                           first_name=first_name, last_name=last_name)
