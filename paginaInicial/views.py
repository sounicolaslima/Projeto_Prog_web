from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from freelancers.models import Freelancer
from escalas.models import Escala
from pagamentos.models import Pagamento
from registroDePontos.models import RegistroDePonto
from django.db.models import Count, Sum, Q
from datetime import datetime, date, timedelta
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required 
def dashboard(request):
    if hasattr(request.user, 'perfilusuario'):
        if request.user.perfilusuario.tipo == 'freelancer':
            return redirect('dashboard_freelancer')
    # Calcular estatísticas em tempo real
    hoje = date.today()
    
    # Freelancers
    total_freelancers = Freelancer.objects.count()
    
    # Escalas
    escalas_hoje = Escala.objects.filter(data=hoje).count()
    
    # Pagamentos
    pagamentos_pendentes = Pagamento.objects.filter(status='pendente').count()
    
    # Registros de ponto
    registros_hoje = RegistroDePonto.objects.filter(
        data_entrada__date=hoje
    ).count()
    
    # Estatísticas adicionais
    total_escalas = Escala.objects.count()
    total_pagamentos = Pagamento.objects.count()
    
    # Próximas escalas (próximos 3 dias)
    proximos_dias = hoje + timedelta(days=3)
    proximas_escalas = Escala.objects.filter(
        data__range=[hoje, proximos_dias]
    ).order_by('data', 'horario_inicio')[:5]
    
    # Últimos pagamentos
    ultimos_pagamentos = Pagamento.objects.all().order_by('-id')[:5]
    
    # Freelancers ativos (com escalas hoje)
    freelancers_ativos_hoje = Freelancer.objects.filter(
        escala__data=hoje
    ).distinct().count()
    
    context = {
        'total_freelancers': total_freelancers,
        'escalas_hoje': escalas_hoje,
        'pagamentos_pendentes': pagamentos_pendentes,
        'registros_hoje': registros_hoje,
        'total_escalas': total_escalas,
        'total_pagamentos': total_pagamentos,
        'proximas_escalas': proximas_escalas,
        'ultimos_pagamentos': ultimos_pagamentos,
        'freelancers_ativos_hoje': freelancers_ativos_hoje,
    }
    
    return render(request, "paginaInicial/dashboard.html", context)
