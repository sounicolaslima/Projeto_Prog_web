from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
from .models import Freelancer

@login_required 
def listar_freelancers(request):
    query = request.GET.get('q', '') 
    freelancers = Freelancer.objects.all()

    if query:
        freelancers = freelancers.filter(
            nome__icontains=query
        ) 

    return render(request, "freelancers/listar_freelancers.html", 
    
    {"freelancers": freelancers, "query": query })

@login_required 
def cadastrar_freelancer(request):
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
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    return render(request, "freelancers/visualizar_freelancer.html", {
        "freelancer": freelancer
    })

@login_required
def editar_freelancer(request, freelancer_id):
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