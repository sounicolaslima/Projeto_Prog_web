from django.urls import path
from . import views

urlpatterns = [
    path("", views.listar_escalas, name="listar_escalas"),
    path("cadastrar/", views.cadastrar_escala, name="cadastrar_escala"),
]
