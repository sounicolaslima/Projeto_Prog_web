from django.db import models
from freelancers.models import Freelancer
from datetime import datetime, time, date

class Escala(models.Model):
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE)
    data = models.DateField()
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()

    def __str__(self):
        return f"{self.freelancer.nome} - {self.data}"

    @property
    def duracao(self):
        """Calcula a duração em horas"""
        inicio = datetime.combine(date.today(), self.horario_inicio)
        fim = datetime.combine(date.today(), self.horario_fim)
        
        if fim < inicio:
            fim = datetime.combine(date.today(), self.horario_fim)
            fim = fim.replace(day=fim.day + 1)
        
        diferenca = fim - inicio
        horas = diferenca.total_seconds() / 3600
        return round(horas, 2)

    @property
    def status(self):
        """Define o status automaticamente baseado na data e hora atual"""
        agora = datetime.now()
        data_hora_inicio = datetime.combine(self.data, self.horario_inicio)
        data_hora_fim = datetime.combine(self.data, self.horario_fim)
        
        if data_hora_fim < data_hora_inicio:
            data_hora_fim = data_hora_fim.replace(day=data_hora_fim.day + 1)
        
        if agora < data_hora_inicio:
            return "Agendada"
        elif data_hora_inicio <= agora <= data_hora_fim:
            return "Em Andamento"
        else:
            return "Concluída"

