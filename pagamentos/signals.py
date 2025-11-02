from django.db.models.signals import post_save
from django.dispatch import receiver
from registroDePontos.models import RegistroDePonto
from .models import Pagamento
from datetime import datetime, timedelta
from django.utils import timezone

@receiver(post_save, sender=RegistroDePonto)
def criar_ou_atualizar_pagamento(sender, instance, **kwargs):
    """
    Cria ou atualiza pagamento automaticamente quando um registro de ponto é concluído
    """
    if instance.data_saida:  # Só processa registros concluídos
        freelancer = instance.freelancer
        data_registro = instance.data_entrada.date()
        
        # Definir período (semana atual)
        inicio_semana = data_registro - timedelta(days=data_registro.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        
        # Buscar ou criar pagamento para o período
        pagamento, created = Pagamento.objects.get_or_create(
            freelancer=freelancer,
            periodo_inicio=inicio_semana,
            periodo_fim=fim_semana,
            defaults={
                'valor_total': 0,
                'valor_pago': 0,
                'valor_pendente': 0,
                'horas_trabalhadas': 0
            }
        )
        
        # Atualizar pagamento com novos cálculos
        pagamento.atualizar_pagamento()