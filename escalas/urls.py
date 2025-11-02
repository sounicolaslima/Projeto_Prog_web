from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_escalas, name='listar_escalas'),
    path('cadastrar/', views.cadastrar_escala, name='cadastrar_escala'),
    path('<int:escala_id>/visualizar/', views.visualizar_escala, name='visualizar_escala'),
    path('<int:escala_id>/editar/', views.editar_escala, name='editar_escala'),
    path('<int:escala_id>/excluir/', views.excluir_escala, name='excluir_escala'),
]
