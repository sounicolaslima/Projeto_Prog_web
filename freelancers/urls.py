from django.urls import path
from . import views

urlpatterns = [
    path("", views.listar_freelancers, name="listar_freelancers"),
    path("cadastrar/", views.cadastrar_freelancer, name="cadastrar_freelancer"),
    path('<int:freelancer_id>/visualizar/', views.visualizar_freelancer, name='visualizar_freelancer'), 
    path('<int:freelancer_id>/editar/', views.editar_freelancer, name='editar_freelancer'), 
]