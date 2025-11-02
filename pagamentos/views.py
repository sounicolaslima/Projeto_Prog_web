from decimal import InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Pagamento
from django.contrib import messages
from freelancers.models import Freelancer
from django.db.models import Sum, Q
from datetime import datetime, date, timedelta

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
    total_parciais = pagamentos.filter(status='pago_parcial').count()

    # Calcular valores
    valor_total_pago = pagamentos.filter(status='pago').aggregate(
        total=Sum('valor_pago')
    )['total'] or 0

    valor_total_pendente = pagamentos.filter(status__in=['pendente', 'pago_parcial']).aggregate(
        total=Sum('valor_pendente')
    )['total'] or 0

    valor_total_geral = pagamentos.aggregate(
        total=Sum('valor_total')
    )['total'] or 0

    freelancers = Freelancer.objects.all()

    return render(request, "pagamentos/listar_pagamentos.html", {
        "pagamentos": pagamentos,
        "freelancers": freelancers,
        "status_filter": status_filter,
        "freelancer_filter": freelancer_filter,
        "total_pagamentos": total_pagamentos,
        "total_pagos": total_pagos,
        "total_pendentes": total_pendentes,
        "total_parciais": total_parciais,
        "valor_total_pago": valor_total_pago,
        "valor_total_pendente": valor_total_pendente,
        "valor_total_geral": valor_total_geral,
    })

@login_required
def visualizar_pagamento(request, pagamento_id):
    pagamento = get_object_or_404(Pagamento, id=pagamento_id)
    
    # Buscar registros de ponto do período
    from registroDePontos.models import RegistroDePonto
    registros_ponto = RegistroDePonto.objects.filter(
        freelancer=pagamento.freelancer,
        data_entrada__date__gte=pagamento.periodo_inicio,
        data_entrada__date__lte=pagamento.periodo_fim,
        data_saida__isnull=False
    ).order_by('-data_entrada')
    
    return render(request, "pagamentos/visualizar_pagamento.html", {
        "pagamento": pagamento,
        "registros_ponto": registros_ponto
    })

@login_required
def pagar_freelancer(request, pagamento_id):
    """View para realizar pagamento ao freelancer"""
    pagamento = get_object_or_404(Pagamento, id=pagamento_id)

    if request.method == 'POST':
        valor_pago = request.POST.get('valor_pago', 0)
        
        try:
            valor_pago = float(valor_pago)
            if valor_pago <= 0:
                messages.error(request, 'O valor do pagamento deve ser maior que zero!')
            elif valor_pago > pagamento.valor_pendente:
                messages.error(request, f'O valor não pode ser maior que R$ {pagamento.valor_pendente} (valor pendente)!')
            else:
                pagamento.registrar_pagamento(valor_pago)
                
                if pagamento.status == 'pago':
                    messages.success(request, f'Pagamento completo de R$ {valor_pago:.2f} realizado para {pagamento.freelancer.nome}! Status: PAGO')
                else:
                    messages.success(request, f'Pagamento parcial de R$ {valor_pago:.2f} realizado para {pagamento.freelancer.nome}. Restante: R$ {pagamento.valor_pendente:.2f}')
                
                return redirect('listar_pagamentos')
                
        except ValueError:
            messages.error(request, 'Valor inválido! Digite um número válido.')

    return render(request, 'pagamentos/pagar_freelancer.html', {
        'pagamento': pagamento,
    })

@login_required
def cancelar_pagamento(request, pagamento_id):
    """View para cancelar um pagamento realizado"""
    pagamento = get_object_or_404(Pagamento, id=pagamento_id)
    
    if request.method == 'POST':
        if pagamento.valor_pago > 0:
            freelancer_nome = pagamento.freelancer.nome
            valor_pago = pagamento.valor_pago
            
            # Zerar o valor pago e atualizar status para pendente
            pagamento.valor_pago = 0
            pagamento.status = 'pendente'
            pagamento.valor_pendente = pagamento.valor_total
            pagamento.save()
            
            messages.success(request, f'Pagamento de {freelancer_nome} cancelado com sucesso! Valor de R$ {valor_pago:.2f} retornou para pendente.')
        else:
            messages.warning(request, 'Este pagamento não possui valores pagos para cancelar.')
        
        return redirect('listar_pagamentos')
    
    # Se não for POST, redirecionar para visualizar o pagamento
    return redirect('visualizar_pagamento', pagamento_id=pagamento.id)

@login_required
def pagar_freelancer(request, pagamento_id):
    """View para realizar pagamento ao freelancer"""
    pagamento = get_object_or_404(Pagamento, id=pagamento_id)
    
    # Buscar registros de ponto do período
    from registroDePontos.models import RegistroDePonto
    registros_ponto = RegistroDePonto.objects.filter(
        freelancer=pagamento.freelancer,
        data_entrada__date__gte=pagamento.periodo_inicio,
        data_entrada__date__lte=pagamento.periodo_fim,
        data_saida__isnull=False
    ).order_by('-data_entrada')

    if request.method == 'POST':
        valor_pago = request.POST.get('valor_pago', 0)
        
        try:
            # CORREÇÃO: Já converter para Decimal aqui também
            from decimal import Decimal
            valor_pago_decimal = Decimal(valor_pago)  # ← Converter direto para Decimal
            
            if valor_pago_decimal <= 0:
                messages.error(request, 'O valor do pagamento deve ser maior que zero!')
            elif valor_pago_decimal > pagamento.valor_pendente:
                messages.error(request, f'O valor não pode ser maior que R$ {pagamento.valor_pendente} (valor pendente)!')
            else:
                pagamento.registrar_pagamento(valor_pago_decimal)  # ← Agora passa Decimal
                
                if pagamento.status == 'pago':
                    messages.success(request, f'✅ Pagamento completo de R$ {valor_pago_decimal:.2f} realizado para {pagamento.freelancer.nome}! Status: PAGO')
                else:
                    messages.success(request, f'⚠️ Pagamento parcial de R$ {valor_pago_decimal:.2f} realizado para {pagamento.freelancer.nome}. Restante: R$ {pagamento.valor_pendente:.2f}')
                
                return redirect('listar_pagamentos')
                
        except (ValueError, InvalidOperation):
            messages.error(request, 'Valor inválido! Digite um número válido.')

    return render(request, 'pagamentos/pagar_freelancer.html', {
        'pagamento': pagamento,
        'registros_ponto': registros_ponto
    })
