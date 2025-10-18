from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import RegistroDePonto
from freelancers.models import Freelancer
from django.utils import timezone

@login_required 
def listar_pontos(request, freelancer_id):
    # Buscar todos os freelancers para o seletor
    todos_freelancers = Freelancer.objects.all()
    
    # Se não tem freelancer_id válido, pega o primeiro
    if not freelancer_id and todos_freelancers.exists():
        primeiro_freelancer = todos_freelancers.first()
        return redirect("listar_pontos", freelancer_id=primeiro_freelancer.id)
    
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    pontos = RegistroDePonto.objects.filter(freelancer=freelancer).order_by('-data_entrada')
    
    # Calcular estatísticas
    total_pontos = pontos.count()
    pontos_concluidos = pontos.filter(data_saida__isnull=False).count()
    pontos_andamento = pontos.filter(data_saida__isnull=True).count()
    
    return render(request, "pontos/listar_pontos.html", {
        "freelancer": freelancer, 
        "todos_freelancers": todos_freelancers,
        "pontos": pontos,
        "total_pontos": total_pontos,
        "pontos_concluidos": pontos_concluidos,
        "pontos_andamento": pontos_andamento
    })

@login_required 
def registrar_ponto(request, freelancer_id):
    # Buscar todos os freelancers para o seletor
    todos_freelancers = Freelancer.objects.all()
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    
    # Se mudou o freelancer no seletor
    if request.method == "POST" and 'freelancer' in request.POST:
        novo_freelancer_id = request.POST.get("freelancer")
        if novo_freelancer_id and novo_freelancer_id != str(freelancer.id):
            return redirect("registrar_ponto", freelancer_id=novo_freelancer_id)
    
    # Verificar se tem registro em andamento
    registro_andamento = RegistroDePonto.objects.filter(
        freelancer=freelancer, 
        data_saida__isnull=True
    ).last()
    
    if request.method == "POST":
        acao = request.POST.get("acao")
        if acao == "entrada":
            RegistroDePonto.objects.create(freelancer=freelancer, data_entrada=timezone.now())
        elif acao == "saida":
            if registro_andamento:
                registro_andamento.data_saida = timezone.now()
                registro_andamento.save()
        return redirect("listar_pontos", freelancer_id=freelancer.id)

    return render(request, "pontos/registrar_ponto.html", {
        "freelancer": freelancer,
        "todos_freelancers": todos_freelancers,
        "registro_andamento": registro_andamento
    })