from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Freelancer
from django.utils import timezone
from datetime import date
from escalas.models import Escala
from registroDePontos.models import RegistroDePonto
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from pagamentos.models import Pagamento 
from django.db import models

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
        tipo_usuario = request.POST.get("tipo_usuario", "freelancer")
        senha = request.POST.get("senha")

        # VALIDAÇÃO DA SENHA
        if not senha or len(senha) < 6:
            messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
            return render(request, "freelancers/cadastrar_freelancer.html")

        # Criar o freelancer
        freelancer = Freelancer.objects.create(
            nome=nome, cpf=cpf, contato=contato,
            valor_hora=valor_hora, status=status
        )

        # Criar usuário e perfil
        username = cpf.replace('.', '').replace('-', '')

        # Verificar se o username já existe
        if User.objects.filter(username=username).exists():
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1

        try:
            user = User.objects.create(
                username=username,
                email=contato if '@' in contato else '',
                password=make_password(senha),
                first_name=nome.split(' ')[0],
                last_name=' '.join(nome.split(' ')[1:]) if len(nome.split(' ')) > 1 else ''
            )

            # Criar perfil de usuário
            from .models import PerfilUsuario
            perfil, created = PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={
                    'freelancer': freelancer if tipo_usuario == 'freelancer' else None,
                    'tipo': tipo_usuario
                }
            )

            # Se o perfil já existia, atualizar
            if not created:
                perfil.freelancer = freelancer if tipo_usuario == 'freelancer' else None
                perfil.tipo = tipo_usuario
                perfil.save()

            messages.success(request, f'{tipo_usuario.title()} {nome} cadastrado com sucesso!')
            return redirect("listar_freelancers")

        except Exception as e:
            freelancer.delete()
            messages.error(request, f'Erro ao cadastrar usuário: {str(e)}')
            return render(request, "freelancers/cadastrar_freelancer.html")

    return render(request, "freelancers/cadastrar_freelancer.html")

@login_required
def redefinir_senha(request, freelancer_id):
    """View para redefinir senha de um usuário"""
    if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.tipo == 'freelancer':
        return redirect('dashboard_freelancer')

    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    
    try:
        perfil = freelancer.perfilusuario
        user = perfil.user
        
        if request.method == "POST":
            nova_senha = request.POST.get("nova_senha")
            confirmar_senha = request.POST.get("confirmar_senha")
            
            if not nova_senha or not confirmar_senha:
                messages.error(request, 'Todos os campos são obrigatórios.')
                return render(request, "freelancers/redefinir_senha.html", {"freelancer": freelancer})
            
            if len(nova_senha) < 6:
                messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
                return render(request, "freelancers/redefinir_senha.html", {"freelancer": freelancer})
            
            if nova_senha != confirmar_senha:
                messages.error(request, 'As senhas não coincidem.')
                return render(request, "freelancers/redefinir_senha.html", {"freelancer": freelancer})
            
            user.set_password(nova_senha)
            user.save()
            
            messages.success(request, f'Senha redefinida com sucesso para {freelancer.nome}!')
            return redirect("visualizar_freelancer", freelancer_id=freelancer.id)
        
        return render(request, "freelancers/redefinir_senha.html", {
            "freelancer": freelancer
        })
        
    except Exception as e:
        messages.error(request, f'Erro ao redefinir senha: {str(e)}')
        return redirect("visualizar_freelancer", freelancer_id=freelancer.id)

@login_required
def visualizar_freelancer(request, freelancer_id):
    if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.tipo == 'freelancer':
        return redirect('dashboard_freelancer')
    
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    
    total_escalas = freelancer.escala_set.count()
    
    pagamentos = freelancer.pagamento_set.all()
    total_pagamentos = sum(p.valor_total for p in pagamentos) if pagamentos else 0
    
    escalas_recentes = freelancer.escala_set.all().order_by('-data')[:5]
    
    return render(request, "freelancers/visualizar_freelancer.html", {
        "freelancer": freelancer,
        "total_escalas": total_escalas,
        "total_pagamentos": total_pagamentos,
        "escalas_recentes": escalas_recentes,
        "horas_mes": 0,
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
        
        tipo_usuario = request.POST.get("tipo_usuario", "freelancer")
        
        from .models import PerfilUsuario
        perfil, created = PerfilUsuario.objects.get_or_create(
            freelancer=freelancer,
            defaults={'tipo': tipo_usuario}
        )
        
        if not created:
            perfil.tipo = tipo_usuario
            perfil.save()
        
        nova_senha = request.POST.get("nova_senha")
        if nova_senha and len(nova_senha) >= 6:
            perfil.user.set_password(nova_senha)
            perfil.user.save()
            messages.success(request, f'Senha alterada com sucesso para {freelancer.nome}!')
        else:
            messages.success(request, f'Freelancer {freelancer.nome} atualizado com sucesso!')
        
        return redirect("visualizar_freelancer", freelancer_id=freelancer.id)
    
    return render(request, "freelancers/editar_freelancer.html", {
        "freelancer": freelancer
    })

@login_required
def excluir_freelancer(request, freelancer_id):
    if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.tipo == 'freelancer':
        return redirect('dashboard_freelancer')
    
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    
    if request.method == "POST":
        nome_freelancer = freelancer.nome
        
        try:
            perfil = freelancer.perfilusuario
            user = perfil.user
            perfil.delete()
            user.delete()
        except:
            pass
        
        freelancer.delete()
        
        messages.success(request, f'Freelancer {nome_freelancer} excluído com sucesso!')
        return redirect("listar_freelancers")
    
    messages.error(request, 'Método não permitido')
    return redirect("visualizar_freelancer", freelancer_id=freelancer.id)

@login_required
def dashboard_freelancer(request):
    """Dashboard principal do freelancer"""
    try:
        freelancer = request.user.perfilusuario.freelancer
    except:
        return render(request, "freelancers/erro.html", {
            "mensagem": "Perfil de freelancer não encontrado."
        })

    hoje = date.today()
    escalas_hoje = Escala.objects.filter(freelancer=freelancer, data=hoje).order_by('horario_inicio')
    proximas_escalas = Escala.objects.filter(freelancer=freelancer, data__gte=hoje).order_by('data')[:5]

    registros_recentes = RegistroDePonto.objects.filter(freelancer=freelancer).order_by('-data_entrada')[:5]

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

    status_filter = request.GET.get('status', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')

    escalas = Escala.objects.filter(freelancer=freelancer).order_by("data", "horario_inicio")

    if data_inicio:
        escalas = escalas.filter(data__gte=data_inicio)

    if data_fim:
        escalas = escalas.filter(data__lte=data_fim)

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

    if request.method == "POST":
        acao = request.POST.get("acao")

        if acao == "entrada":
            RegistroDePonto.objects.create(
                freelancer=freelancer,
                data_entrada=timezone.now()
            )
        elif acao == "saida":
            registro = RegistroDePonto.objects.filter(
                freelancer=freelancer,
                data_saida__isnull=True
            ).last()
            if registro:
                registro.data_saida = timezone.now()
                registro.save()
        return redirect('meus_pontos')

    registros = RegistroDePonto.objects.filter(freelancer=freelancer).order_by('-data_entrada')

    registro_andamento = RegistroDePonto.objects.filter(
        freelancer=freelancer,
        data_saida__isnull=True
    ).first()

    return render(request, "freelancers/meus_pontos.html", {
        "registros": registros,
        "registro_andamento": registro_andamento
    })

@login_required
def meus_pagamentos(request):
    """Lista os pagamentos do freelancer logado"""
    try:
        # Verificar tipo de usuário
        if not hasattr(request.user, 'perfilusuario'):
            messages.error(request, "Perfil não configurado.")
            return redirect('dashboard')
        
        perfil = request.user.perfilusuario
        
        # Se for admin, redirecionar para lista geral
        if perfil.tipo == 'admin':
            return redirect('listar_pagamentos')
        
        # Se for freelancer, buscar seus pagamentos
        elif perfil.tipo == 'freelancer' and hasattr(perfil, 'freelancer'):
            freelancer = perfil.freelancer
            pagamentos = Pagamento.objects.filter(freelancer=freelancer).order_by('-periodo_inicio')
        else:
            messages.error(request, "Perfil de freelancer não encontrado.")
            return redirect('dashboard')
            
    except Exception as e:
        messages.error(request, f"Erro ao carregar pagamentos: {str(e)}")
        return redirect('dashboard_freelancer')
    
    # Calcular totais
    total_pagamentos = pagamentos.count()
    total_pagos = pagamentos.filter(status='pago').count()
    total_pendentes = pagamentos.filter(status='pendente').count()
    total_parciais = pagamentos.filter(status='pago_parcial').count()
    
    # Calcular valores
    valor_total_recebido = sum(float(p.valor_pago) for p in pagamentos)
    valor_total_pendente = sum(float(p.valor_pendente) for p in pagamentos)
    
    return render(request, "freelancers/meus_pagamentos.html", {
        "pagamentos": pagamentos,
        "freelancer": freelancer,
        "total_pagamentos": total_pagamentos,
        "total_pagos": total_pagos,
        "total_pendentes": total_pendentes,
        "total_parciais": total_parciais,
        "valor_total_recebido": valor_total_recebido,
        "valor_total_pendente": valor_total_pendente,
    })