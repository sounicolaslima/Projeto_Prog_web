# escalas/admin.py
from django.contrib import admin
from .models import Escala

class EscalaAdmin(admin.ModelAdmin):
    list_display = ('freelancer', 'data', 'horario_inicio', 'horario_fim', 'status')
    list_filter = ('data', 'freelancer') 
    search_fields = ('freelancer__nome',)
    autocomplete_fields = ['freelancer']

admin.site.register(Escala, EscalaAdmin)