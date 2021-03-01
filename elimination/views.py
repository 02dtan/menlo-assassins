import datetime
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import Count, Subquery
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView

from . import models, forms


class EliminationFormView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = "target.html"
    form_class = forms.EliminateForm
    success_url = reverse_lazy("target")
    success_message = "Successful elimination! You have been assigned a new target..."
    login_url = 'login'

    def form_valid(self, form):
        try:
            target_senior = models.Senior.objects.get(secret_number=form.cleaned_data['secret_number'])
        except models.Senior.DoesNotExist:
            form.add_error('secret_number', 'That is not the secret number of your target!')
            return self.form_invalid(form)
        eliminator_senior = self.request.user
        if models.Elimination.objects.filter(target=target_senior).exists():
            form.add_error("secret_number", "Target already eliminated!")
            return self.form_invalid(form)
        elif target_senior != eliminator_senior.target:
            form.add_error('secret_number', 'That is not the secret number of your target!')
            return self.form_invalid(form)
        with transaction.atomic():
            elimination = models.Elimination.objects.create(target=target_senior, eliminator=eliminator_senior)
            eliminator_new_target = target_senior.target
            target_senior.target = None
            target_senior.save()
            eliminator_senior.target = None if eliminator_new_target == eliminator_senior else eliminator_new_target
            eliminator_senior.save()
            models.EliminationNotification.objects.create(elimination=elimination)
            print(eliminator_senior.first_name, eliminator_senior.last_name, "just eliminated",
                  target_senior.first_name, target_senior.last_name)
        return super().form_valid(form)


def home(request):
    seniors = models.Senior.objects.filter(is_superuser=False)
    dates = models.Elimination.objects.values_list('created_at', flat=True)
    chart_data = [seniors.count() - models.Elimination.objects.filter(created_at__lte=date).count() for date in dates]
    return render(request, "home.html", {
        "seniors": (seniors
                        .annotate(count=Count('eliminations'))
                        .exclude(count=0)
                        .annotate(latest_elimination_time=Subquery(seniors
                                                                   .values('eliminations')
                                                                   .order_by('-eliminations__created_at')[:1]))
                        .order_by("-count", 'latest_elimination_time')
                        .values("count", "first_name", "last_name", "elimination")[:15]),
        "game_updates": models.GameUpdate.objects.order_by("-created_at"),
        "seniors_left": seniors.filter(elimination__isnull=True).count(),
        "notifications": models.EliminationNotification.objects
                  .filter(elimination__created_at__gte=(timezone.now() - datetime.timedelta(hours=18)))
                  .order_by('-elimination__created_at'),
        "labels": json.dumps([date.isoformat() for date in dates]),
        "data": json.dumps(chart_data) if chart_data else None
    })


class ChangeMailSettingsView(LoginRequiredMixin, FormView):
    template_name = "change_mail_settings.html"
    success_url = reverse_lazy("target")
    form_class = forms.EmailSettingsForm
    login_url = 'login'

    def get_form(self, form_class=None):
        if self.request.method == 'GET':
            return forms.EmailSettingsForm(instance=self.request.user, **self.get_form_kwargs())
        return super().get_form(form_class)

    def form_valid(self, form):
        senior = self.request.user
        senior.email_subscribed = form.cleaned_data['email_subscribed']
        if form.cleaned_data['email'] != "":
            senior.email = form.cleaned_data['email']
        senior.save()
        return super().form_valid(form)
