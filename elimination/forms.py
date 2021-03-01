from django import forms

from elimination.models import Senior
from . import models


class EliminateForm(forms.Form):
    secret_number = forms.RegexField(models.SECRET_NUMBER_VALIDATOR.regex, label="Target Secret 5-Digit Number")


class EmailSettingsForm(forms.ModelForm):
    class Meta:
        model = Senior
        fields = ('email', 'email_subscribed')
