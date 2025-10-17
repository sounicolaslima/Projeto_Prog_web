from django.db import models

from django.db import models
from freelancers.models import Freelancer

class Escala(models.Model):
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE)
    data = models.DateField()
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()

    def __str__(self):
        return f"{self.freelancer.nome} - {self.data}"

