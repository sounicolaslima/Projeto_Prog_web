from django.shortcuts import render, redirect
from .models import Freelancer

def listar_freelancers(request):
    freelancers = Freelancer.objects.all()
    return render(request, "freelancers/listar_freelancers.html", {"freelancers": freelancers})

def cadastrar_freelancer(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        cpf = request.POST.get("cpf")
        contato = request.POST.get("contato")
        valor_hora = request.POST.get("valor_hora")
        Freelancer.objects.create(nome=nome, cpf=cpf, contato=contato, valor_hora=valor_hora)
        return redirect("listar_freelancers")
    return render(request, "freelancers/cadastrar_freelancer.html")

