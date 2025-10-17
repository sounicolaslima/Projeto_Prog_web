
from django.shortcuts import render, get_object_or_404, redirect
from .models import RegistroDePonto
from freelancers.models import Freelancer
from django.utils import timezone

def listar_pontos(request, freelancer_id):
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    pontos = RegistroDePonto.objects.filter(freelancer=freelancer).order_by('-data_entrada')
    return render(request, "pontos/listar_pontos.html", {"freelancer": freelancer, "pontos": pontos})

def registrar_ponto(request, freelancer_id):
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    if request.method == "POST":
        acao = request.POST.get("acao")  # "entrada" ou "saida"
        if acao == "entrada":
            RegistroDePonto.objects.create(freelancer=freelancer, data_entrada=timezone.now())
        elif acao == "saida":
            # Pega último registro sem saída
            registro = RegistroDePonto.objects.filter(freelancer=freelancer, data_saida__isnull=True).last()
            if registro:
                registro.data_saida = timezone.now()
                registro.save()
        return redirect("listar_pontos", freelancer_id=freelancer.id)

    return render(request, "pontos/registrar_ponto.html", {"freelancer": freelancer})
