from django.db import models
from freelancers.models import Freelancer

class RegistroDePonto(models.Model):
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE)
    data_entrada = models.DateTimeField()
    data_saida = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.freelancer.nome} - {self.data_entrada} a {self.data_saida}"

