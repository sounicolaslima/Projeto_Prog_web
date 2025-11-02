from django.contrib import admin
from .models import Freelancer, PerfilUsuario

class FreelancerAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'valor_hora', 'status') 
    search_fields = ('nome', 'cpf')
    list_filter = ('status',) 

admin.site.register(Freelancer, FreelancerAdmin)
admin.site.register(PerfilUsuario)