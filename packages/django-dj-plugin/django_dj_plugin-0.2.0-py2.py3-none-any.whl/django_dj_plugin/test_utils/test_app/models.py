# Put your test models here

from django.db import models

from django_dj_plugin.month.models import MonthField


# Create your models here.

class Example(models.Model):
    name = models.CharField(max_length=20, blank=True)
    month = MonthField("Month Value", help_text="some help...")

    def __str__(self):
        return str(self.month)
