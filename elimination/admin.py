from django.contrib import admin

from . import models

admin.site.register(models.Senior)
admin.site.register(models.GameUpdate)
admin.site.register(models.Elimination)
admin.site.register(models.EliminationNotification)
