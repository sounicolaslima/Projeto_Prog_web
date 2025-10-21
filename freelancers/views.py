from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
from .models import Freelancer
from django.utils import timezone
from datetime import date
from escalas.models import Escala
from registroDePontos.models import RegistroDePonto

@login_required 
def listar_freelancers(request):
    query = request.GET.get('q', '') 
    freelancers = Freelancer.objects.all()

    if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.tipo == 'freelancer':
        return redirect('dashboard_freelancer')
    
    if query:
        freelancers = freelancers.filter(
            nome__icontains=query
        ) 

    return render(request, "freelancers/listar_freelancers.html", 
    
    {"freelancers": freelancers, "query": query })

@login_required 
def cadastrar_freelancer(request):
    if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.tipo == 'freelancer':
        return redirect('dashboard_freelancer')
    
    if request.method == "POST":
        nome = request.POST.get("nome")
        cpf = request.POST.get("cpf")
        contato = request.POST.get("contato")
        valor_hora = request.POST.get("valor_hora")
        status = request.POST.get("status", "ativo")  
        
        Freelancer.objects.create(
            nome=nome, cpf=cpf, contato=contato, 
            valor_hora=valor_hora, status=status  
        )
        return redirect("listar_freelancers")
    return render(request, "freelancers/cadastrar_freelancer.html")

@login_required
def visualizar_freelancer(request, freelancer_id):
    if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.tipo == 'freelancer':
        return redirect('dashboard_freelancer')
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    return render(request, "freelancers/visualizar_freelancer.html", {
        "freelancer": freelancer
    })

@login_required
def editar_freelancer(request, freelancer_id):
    if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.tipo == 'freelancer':
        return redirect('dashboard_freelancer')
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    
    if request.method == "POST":
        freelancer.nome = request.POST.get("nome")
        freelancer.cpf = request.POST.get("cpf")
        freelancer.contato = request.POST.get("contato")
        freelancer.valor_hora = request.POST.get("valor_hora")
        freelancer.status = request.POST.get("status") 
        freelancer.save()
        return redirect("listar_freelancers")
    
    return render(request, "freelancers/editar_freelancer.html", {
        "freelancer": freelancer
    })

@login_required
def dashboard_freelancer(request):
    """Dashboard principal do freelancer"""
    try:
        freelancer = request.user.perfilusuario.freelancer
    except:
        return render(request, "freelancers/erro.html", {
            "mensagem": "Perfil de freelancer não encontrado."
        })
    
    # Escalas do freelancer
    hoje = date.today()
    escalas_hoje = Escala.objects.filter(freelancer=freelancer, data=hoje).order_by('horario_inicio')
    proximas_escalas = Escala.objects.filter(freelancer=freelancer, data__gte=hoje).order_by('data')[:5]
    
    # Registros de ponto recentes
    registros_recentes = RegistroDePonto.objects.filter(freelancer=freelancer).order_by('-data_entrada')[:5]
    
    # Verificar se há registro em andamento
    registro_andamento = RegistroDePonto.objects.filter(
        freelancer=freelancer, 
        data_saida__isnull=True
    ).first()
    
    return render(request, "freelancers/dashboard.html", {
        "freelancer": freelancer,
        "escalas_hoje": escalas_hoje,
        "proximas_escalas": proximas_escalas,
        "registros_recentes": registros_recentes,
        "registro_andamento": registro_andamento,
        "hoje": hoje
    })

@login_required
def minhas_escalas(request):
    """Lista todas as escalas do freelancer"""
    try:
        freelancer = request.user.perfilusuario.freelancer
    except:
        return render(request, "freelancers/erro.html", {
            "mensagem": "Perfil de freelancer não encontrado."
        })
    
    # Filtros
    status_filter = request.GET.get('status', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    escalas = Escala.objects.filter(freelancer=freelancer).order_by("data", "horario_inicio")
    
    if data_inicio:
        escalas = escalas.filter(data__gte=data_inicio)
    
    if data_fim:
        escalas = escalas.filter(data__lte=data_fim)
    
    # Filtro por status
    if status_filter:
        escalas_lista = []
        for escala in escalas:
            if escala.status == status_filter:
                escalas_lista.append(escala)
        escalas = escalas_lista
    
    return render(request, "freelancers/minhas_escalas.html", {
        "escalas": escalas,
        "status_filter": status_filter,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
    })

@login_required
def meus_pontos(request):
    """Registrar e visualizar pontos do freelancer"""
    try:
        freelancer = request.user.perfilusuario.freelancer
    except:
        return render(request, "freelancers/erro.html", {
            "mensagem": "Perfil de freelancer não encontrado."
        })
    
    # Registrar ponto
    if request.method == "POST":
        acao = request.POST.get("acao")
        
        if acao == "entrada":
            # Registrar entrada
            RegistroDePonto.objects.create(
                freelancer=freelancer,
                data_entrada=timezone.now()
            )
        elif acao == "saida":
            # Registrar saída no último registro em andamento
            registro = RegistroDePonto.objects.filter(
                freelancer=freelancer,
                data_saida__isnull=True
            ).last()
            if registro:
                registro.data_saida = timezone.now()
                registro.save()
        return redirect('meus_pontos')
    
    # Listar registros
    registros = RegistroDePonto.objects.filter(freelancer=freelancer).order_by('-data_entrada')
    
    # Verificar se há registro em andamento
    registro_andamento = RegistroDePonto.objects.filter(
        freelancer=freelancer, 
        data_saida__isnull=True
    ).first()
    
    return render(request, "freelancers/meus_pontos.html", {
        "registros": registros,
        "registro_andamento": registro_andamento
    })

