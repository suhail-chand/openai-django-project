from django.contrib import admin
from .models import AIModel


class AIModelAdmin(admin.ModelAdmin):
    list_display = ['model_id', 'max_tokens', 'compatibility']


# Register your models here.
admin.site.register(AIModel, AIModelAdmin)
