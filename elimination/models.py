import random

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

NAME_FIELD_VALIDATOR = RegexValidator(r'^[a-zA-Z]+$')

SECRET_NUMBER_VALIDATOR = RegexValidator(r'^\d{5}$')

STUDENT_ID_VALIDATOR = RegexValidator(r'^\d{8}$')


def get_new_secret_number():
    secret_number = ""
    try:
        existing_secret_number_list = list(Senior.objects.values_list("secret_number", flat=True))
    except:
        # Occurs when we first initialize the database and there is not a table for seniors
        existing_secret_number_list = []
    for existing_secret_number in range(0, 5):
        secret_number += str(random.randrange(10))
    for existing_secret_number in existing_secret_number_list:
        if secret_number == existing_secret_number:
            return get_new_secret_number()
    return secret_number


class Senior(AbstractUser):
    target = models.OneToOneField('Senior', models.SET_NULL, null=True, blank=True)
    username_validator = STUDENT_ID_VALIDATOR
    first_name = models.CharField(max_length=64, validators=[NAME_FIELD_VALIDATOR])
    last_name = models.CharField(max_length=64, validators=[NAME_FIELD_VALIDATOR])
    secret_number = models.CharField(default=get_new_secret_number, max_length=5, validators=[SECRET_NUMBER_VALIDATOR],
                                     unique=True)
    initial_password = models.CharField(max_length=5, validators=[RegexValidator(r'^[A-Z]{5}$')])
    email_subscribed = models.BooleanField(default=True)

    def clean(self):
        if self.target == self:
            raise ValidationError("Can't have yourself as a target")


Senior._meta.get_field('username').verbose_name = 'Student ID'


class Elimination(models.Model):
    target = models.OneToOneField('Senior', models.SET_NULL, null=True)
    eliminator = models.ForeignKey('Senior', models.SET_NULL, null=True, related_name='eliminations')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.target == self.eliminator:
            raise ValidationError("Can't eliminate yourself")


class GameUpdate(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, )


class EliminationNotification(models.Model):
    elimination = models.ForeignKey(Elimination, models.CASCADE)
