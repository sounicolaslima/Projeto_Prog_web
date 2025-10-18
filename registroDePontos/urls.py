from django.urls import path
from . import views

urlpatterns = [
    path("<int:freelancer_id>/listar/", views.listar_pontos, name="listar_pontos"),
    path("<int:freelancer_id>/registrar/", views.registrar_ponto, name="registrar_ponto"),
]

