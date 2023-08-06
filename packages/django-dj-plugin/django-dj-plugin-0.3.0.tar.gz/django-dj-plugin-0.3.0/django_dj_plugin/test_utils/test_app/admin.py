from django.contrib import admin

# Put your models admin models here
from .models import Example


@admin.register(Example)
class ExampleAdmin(admin.ModelAdmin):
    pass
