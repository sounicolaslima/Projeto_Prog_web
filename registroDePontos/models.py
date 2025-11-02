from django.db import models
from freelancers.models import Freelancer

class RegistroDePonto(models.Model):
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE)
    data_entrada = models.DateTimeField()
    data_saida = models.DateTimeField(null=True, blank=True)

    def duracao(self):
        """Calcula a duração entre entrada e saída"""
        if self.data_saida:
            diferenca = self.data_saida - self.data_entrada
            horas = int(diferenca.total_seconds() // 3600)
            minutos = int((diferenca.total_seconds() % 3600) // 60)
            return f"{horas}h {minutos}min"
        return "Em andamento"
    
    def status(self):
        """Retorna o status do registro"""
        if self.data_saida:
            return "concluido"
        return "andamento"

    def __str__(self):
        return f"{self.freelancer.nome} - {self.data_entrada} a {self.data_saida}"