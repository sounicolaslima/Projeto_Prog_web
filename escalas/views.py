from django.shortcuts import render

from django.shortcuts import render, redirect
from .models import Escala
from freelancers.models import Freelancer

def listar_escalas(request):
    escalas = Escala.objects.all().order_by("data", "horario_inicio")
    return render(request, "escalas/listar_escalas.html", {"escalas": escalas})

def cadastrar_escala(request):
    freelancers = Freelancer.objects.all()
    if request.method == "POST":
        freelancer_id = request.POST.get("freelancer")
        data = request.POST.get("data")
        inicio = request.POST.get("horario_inicio")
        fim = request.POST.get("horario_fim")
        Escala.objects.create(
            freelancer=Freelancer.objects.get(id=freelancer_id),
            data=data,
            horario_inicio=inicio,
            horario_fim=fim
        )
        return redirect("listar_escalas")
    return render(request, "escalas/cadastrar_escala.html", {"freelancers": freelancers})

