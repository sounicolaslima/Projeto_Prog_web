from django.urls import path
from . import views

urlpatterns = [
    path("", views.listar_freelancers, name="listar_freelancers"),
    path("cadastrar/", views.cadastrar_freelancer, name="cadastrar_freelancer"),
    path('<int:freelancer_id>/visualizar/', views.visualizar_freelancer, name='visualizar_freelancer'), 
    path('<int:freelancer_id>/editar/', views.editar_freelancer, name='editar_freelancer'), 
    path('<int:freelancer_id>/excluir/', views.excluir_freelancer, name='excluir_freelancer'),
    path('<int:freelancer_id>/redefinir-senha/', views.redefinir_senha, name='redefinir_senha'), 

    path("dashboard/", views.dashboard_freelancer, name="dashboard_freelancer"),
    path("minhas-escalas/", views.minhas_escalas, name="minhas_escalas"),
    path("meus-pontos/", views.meus_pontos, name="meus_pontos"),
    path("meus_pagamentos/", views.meus_pagamentos, name="meus_pagamentos"),

]