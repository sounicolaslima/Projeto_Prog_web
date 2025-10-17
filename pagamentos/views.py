from django.shortcuts import render, redirect
from .models import Pagamento
from freelancers.models import Freelancer

def listar_pagamentos(request):
    pagamentos = Pagamento.objects.all().order_by("-periodo_inicio")
    return render(request, "pagamentos/listar_pagamentos.html", {"pagamentos": pagamentos})

def cadastrar_pagamento(request):
    freelancers = Freelancer.objects.all()
    if request.method == "POST":
        freelancer_id = request.POST.get("freelancer")
        periodo_inicio = request.POST.get("periodo_inicio")
        periodo_fim = request.POST.get("periodo_fim")
        valor = request.POST.get("valor")
        status = request.POST.get("status")

        Pagamento.objects.create(
            freelancer=Freelancer.objects.get(id=freelancer_id),
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            valor_calculado=valor,
            status=status
        )
        return redirect("listar_pagamentos")

    return render(request, "pagamentos/cadastrar_pagamento.html", {"freelancers": freelancers})
