from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Pagamento
from django.contrib import messages 
from freelancers.models import Freelancer
from django.db.models import Sum, Q
from datetime import datetime

@login_required
def listar_pagamentos(request):
    # Filtros
    status_filter = request.GET.get('status', '')
    freelancer_filter = request.GET.get('freelancer', '')
    
    pagamentos = Pagamento.objects.all().order_by('-periodo_inicio')
    
    # Aplicar filtros
    if status_filter:
        pagamentos = pagamentos.filter(status=status_filter)
    if freelancer_filter:
        pagamentos = pagamentos.filter(freelancer_id=freelancer_filter)
    
    # Calcular totais
    total_pagamentos = pagamentos.count()
    total_pagos = pagamentos.filter(status='pago').count()
    total_pendentes = pagamentos.filter(status='pendente').count()
    
    # Calcular valores
    valor_total_pago = pagamentos.filter(status='pago').aggregate(
        total=Sum('valor_calculado')
    )['total'] or 0
    
    valor_total_pendente = pagamentos.filter(status='pendente').aggregate(
        total=Sum('valor_calculado')
    )['total'] or 0
    
    valor_total_geral = valor_total_pago + valor_total_pendente
    
    freelancers = Freelancer.objects.all()
    
    return render(request, "pagamentos/listar_pagamentos.html", {
        "pagamentos": pagamentos,
        "freelancers": freelancers,
        "status_filter": status_filter,
        "freelancer_filter": freelancer_filter,
        "total_pagamentos": total_pagamentos,
        "total_pagos": total_pagos,
        "total_pendentes": total_pendentes,
        "valor_total_pago": valor_total_pago,
        "valor_total_pendente": valor_total_pendente,
        "valor_total_geral": valor_total_geral,
    })

@login_required
def cadastrar_pagamento(request):
    freelancers = Freelancer.objects.all()
    
    if request.method == "POST":
        freelancer_id = request.POST.get("freelancer")
        periodo_inicio = request.POST.get("periodo_inicio")
        periodo_fim = request.POST.get("periodo_fim")
        status = request.POST.get("status")

        freelancer = Freelancer.objects.get(id=freelancer_id)
        
        # Criar pagamento vazio primeiro
        pagamento = Pagamento.objects.create(
            freelancer=freelancer,
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            valor_calculado=0,  # Será calculado automaticamente
            status=status
        )
        
        # Calcular horas e valor automaticamente
        horas_trabalhadas = pagamento.calcular_horas_trabalhadas()
        valor_calculado = pagamento.calcular_valor_pagamento()
        
        # Atualizar com os valores calculados
        pagamento.horas_trabalhadas = horas_trabalhadas
        pagamento.valor_calculado = valor_calculado
        pagamento.save()

        messages.success(request, f'Pagamento de {freelancer.nome} cadastrado com sucesso!')
        return redirect("listar_pagamentos")

    return render(request, "pagamentos/cadastrar_pagamento.html", {"freelancers": freelancers})

@login_required
def visualizar_pagamento(request, pagamento_id):
    pagamento = get_object_or_404(Pagamento, id=pagamento_id)
    return render(request, "pagamentos/visualizar_pagamento.html", {
        "pagamento": pagamento
    })

@login_required
def editar_pagamento(request, pagamento_id):
    pagamento = get_object_or_404(Pagamento, id=pagamento_id)
    freelancers = Freelancer.objects.all()
    
    if request.method == 'POST':
        # Processar os dados do formulário
        freelancer_id = request.POST.get('freelancer')
        periodo_inicio = request.POST.get('periodo_inicio')
        periodo_fim = request.POST.get('periodo_fim')
        valor = request.POST.get('valor')
        status = request.POST.get('status')
        
        # Atualizar o objeto
        pagamento.freelancer = Freelancer.objects.get(id=freelancer_id)
        pagamento.periodo_inicio = periodo_inicio
        pagamento.periodo_fim = periodo_fim
        pagamento.valor_calculado = valor
        pagamento.status = status
        
        pagamento.save()
        
        messages.success(request, f'Pagamento de {pagamento.freelancer.nome} atualizado com sucesso!')
        return redirect('visualizar_pagamento', pagamento_id=pagamento.id)
    
    # Se for GET, mostrar o formulário preenchido
    context = {
        'pagamento': pagamento,
        'freelancers': freelancers,
    }
    return render(request, 'pagamentos/editar_pagamento.html', context)

@login_required
def excluir_pagamento(request, pagamento_id):
    pagamento = get_object_or_404(Pagamento, id=pagamento_id)
    
    if request.method == 'POST':
        freelancer_nome = pagamento.freelancer.nome
        pagamento.delete()
        messages.success(request, f'Pagamento de {freelancer_nome} excluído com sucesso!')
        return redirect('listar_pagamentos')
    
    # Se não for POST, redireciona para a lista
    return redirect('listar_pagamentos')