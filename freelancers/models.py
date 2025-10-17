from django.db import models

from django.db import models

class Freelancer(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    contato = models.CharField(max_length=50)
    valor_hora = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.nome

