from django.db import models
from freelancers.models import Freelancer
from registroDePontos.models import RegistroDePonto
from django.db.models import Sum
from datetime import datetime, date
from django.utils import timezone
from decimal import Decimal  # ← IMPORTANTE: garantir que está importado

class Pagamento(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago_parcial', 'Pago Parcialmente'),
        ('pago', 'Pago'),
    ]
    
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE)
    periodo_inicio = models.DateField()
    periodo_fim = models.DateField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_pendente = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    horas_trabalhadas = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-periodo_inicio']

    def calcular_horas_trabalhadas(self):
        """Calcula horas trabalhadas no período baseado nos registros de ponto"""
        registros = RegistroDePonto.objects.filter(
            freelancer=self.freelancer,
            data_entrada__date__gte=self.periodo_inicio,
            data_entrada__date__lte=self.periodo_fim,
            data_saida__isnull=False
        )

        total_segundos = 0
        for registro in registros:
            if registro.data_saida:
                diferenca = registro.data_saida - registro.data_entrada
                total_segundos += diferenca.total_seconds()

        total_horas = total_segundos / 3600
        return round(total_horas, 2)

    def calcular_valor_total(self):
        """Calcula valor total baseado nas horas trabalhadas"""
        horas = self.calcular_horas_trabalhadas()
        horas_decimal = Decimal(str(horas))  # ← Converter para Decimal
        valor_total = horas_decimal * self.freelancer.valor_hora
        return valor_total

    def atualizar_pagamento(self):
        """Atualiza automaticamente os valores do pagamento"""
        self.horas_trabalhadas = self.calcular_horas_trabalhadas()
        self.valor_total = self.calcular_valor_total()
        self.valor_pendente = self.valor_total - self.valor_pago

        # Atualizar status automaticamente
        if self.valor_pago == 0:
            self.status = 'pendente'
        elif self.valor_pago >= self.valor_total:
            self.status = 'pago'
        else:
            self.status = 'pago_parcial'

        self.save()

    def registrar_pagamento(self, valor_pago):
        """Registra um pagamento realizado"""
        # CORREÇÃO: Converter para Decimal antes de somar
        valor_pago_decimal = Decimal(str(valor_pago))  # ← AQUI ESTÁ A CORREÇÃO
        self.valor_pago += valor_pago_decimal
        self.atualizar_pagamento()

    def __str__(self):
        return f"{self.freelancer.nome} - {self.periodo_inicio} a {self.periodo_fim} - R$ {self.valor_total}"

    def save(self, *args, **kwargs):
        # Se for um novo pagamento, calcular automaticamente
        if not self.pk:
            self.horas_trabalhadas = self.calcular_horas_trabalhadas()
            self.valor_total = self.calcular_valor_total()
            self.valor_pendente = self.valor_total

        super().save(*args, **kwargs)