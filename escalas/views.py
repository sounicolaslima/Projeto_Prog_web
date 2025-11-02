from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.db.models import Count, Q
from .models import Escala
from freelancers.models import Freelancer

@login_required
def listar_escalas(request):
    if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.tipo == 'freelancer':
        return redirect('dashboard_freelancer')
    
    # Filtros
    freelancer_filter = request.GET.get('freelancer', '')
    status_filter = request.GET.get('status', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    escalas = Escala.objects.all().order_by("data", "horario_inicio")
    
    # Aplicar filtros (manter como QuerySet)
    if freelancer_filter:
        escalas = escalas.filter(freelancer_id=freelancer_filter)
    
    if data_inicio:
        escalas = escalas.filter(data__gte=data_inicio)
    
    if data_fim:
        escalas = escalas.filter(data__lte=data_fim)
    
    # Filtro por status (aplicar depois de todos os outros filtros)
    if status_filter:
        escalas_lista = []
        for escala in escalas:
            if escala.status == status_filter:
                escalas_lista.append(escala)
        escalas = escalas_lista  # Agora é uma lista, mas já aplicamos todos os filtros anteriores
    
    # Calcular totais (usar o QuerySet original para os totais)
    hoje = date.today()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    inicio_mes = hoje.replace(day=1)
    
    total_escalas = Escala.objects.count()
    escalas_hoje = Escala.objects.filter(data=hoje).count()
    escalas_semana = Escala.objects.filter(data__range=[inicio_semana, fim_semana]).count()
    escalas_mes = Escala.objects.filter(data__year=hoje.year, data__month=hoje.month).count()
    freelancers_ativos = Freelancer.objects.count()
    
    # Próximos 7 dias para o calendário
    proximos_dias = []
    for i in range(7):
        dia = hoje + timedelta(days=i)
        total_dia = Escala.objects.filter(data=dia).count()
        proximos_dias.append({
            'data': dia,
            'total_escalas': total_dia
        })
    
    freelancers = Freelancer.objects.all()
    
    return render(request, "escalas/listar_escalas.html", {
        "escalas": escalas,
        "freelancers": freelancers,
        "total_escalas": total_escalas,
        "escalas_hoje": escalas_hoje,
        "escalas_semana": escalas_semana,
        "escalas_mes": escalas_mes,
        "freelancers_ativos": freelancers_ativos,
        "proximos_dias": proximos_dias,
        "freelancer_filter": freelancer_filter,
        "status_filter": status_filter,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
    })

@login_required
def cadastrar_escala(request):
    freelancers = Freelancer.objects.all()
    
    # Próximas escalas para o preview
    hoje = date.today()
    proximas_escalas = Escala.objects.filter(data__gte=hoje).order_by('data')[:3]
    
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
        
        messages.success(request, 'Escala cadastrada com sucesso!')
        return redirect("listar_escalas")
    
    return render(request, "escalas/cadastrar_escala.html", {
        "freelancers": freelancers,
        "proximas_escalas": proximas_escalas
    })

@login_required
def visualizar_escala(request, escala_id):
    escala = get_object_or_404(Escala, id=escala_id)
    return render(request, "escalas/visualizar_escala.html", {
        "escala": escala
    })

@login_required
def editar_escala(request, escala_id):
    escala = get_object_or_404(Escala, id=escala_id)
    freelancers = Freelancer.objects.all()
    
    if request.method == "POST":
        freelancer_id = request.POST.get("freelancer")
        data = request.POST.get("data")
        inicio = request.POST.get("horario_inicio")
        fim = request.POST.get("horario_fim")
        
        escala.freelancer = Freelancer.objects.get(id=freelancer_id)
        escala.data = data
        escala.horario_inicio = inicio
        escala.horario_fim = fim
        escala.save()
        
        messages.success(request, 'Escala atualizada com sucesso!')
        return redirect("listar_escalas")
    
    return render(request, "escalas/editar_escala.html", {
        "escala": escala,
        "freelancers": freelancers
    })

@login_required
def excluir_escala(request, escala_id):
    escala = get_object_or_404(Escala, id=escala_id)
    
    if request.method == "POST":
        escala.delete()
        messages.success(request, 'Escala excluída com sucesso!')
        return redirect("listar_escalas")
    
    return redirect("listar_escalas")