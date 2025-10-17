from django.urls import path
from . import views

urlpatterns = [
    path("", views.listar_freelancers, name="listar_freelancers"),
    path("cadastrar/", views.cadastrar_freelancer, name="cadastrar_freelancer"),
]