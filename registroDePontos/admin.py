from django.contrib import admin
from .models import RegistroDePonto

class RegistroDePontoAdmin(admin.ModelAdmin):
    list_display = ('freelancer', 'data_entrada', 'data_saida', 'duracao', 'status')
    list_filter = ('freelancer', 'data_entrada')
    search_fields = ('freelancer__nome',)

admin.site.register(RegistroDePonto, RegistroDePontoAdmin)
