from django.db import models
from freelancers.models import Freelancer
from registroDePontos.models import RegistroDePonto
from django.db.models import Sum
from datetime import datetime

class Pagamento(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
    ]
    
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE)
    periodo_inicio = models.DateField()
    periodo_fim = models.DateField()
    valor_calculado = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    # REMOVA data_criacao - esta linha não é necessária
    horas_trabalhadas = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def calcular_horas_trabalhadas(self):
        """Calcula horas trabalhadas no período"""
        registros = RegistroDePonto.objects.filter(
            freelancer=self.freelancer,
            data_entrada__date__gte=self.periodo_inicio,
            data_entrada__date__lte=self.periodo_fim,
            data_saida__isnull=False  # Só registros completos
        )
        
        total_horas = 0
        for registro in registros:
            if registro.data_saida:
                diferenca = registro.data_saida - registro.data_entrada
                horas = diferenca.total_seconds() / 3600  # Converter para horas
                total_horas += horas
        
        return round(total_horas, 2)

    def calcular_valor_pagamento(self):
        """Calcula valor baseado nas horas trabalhadas"""
        horas = self.calcular_horas_trabalhadas()
        return horas * self.freelancer.valor_hora

    def __str__(self):
        return f"{self.freelancer.nome} - {self.periodo_inicio} a {self.periodo_fim}"