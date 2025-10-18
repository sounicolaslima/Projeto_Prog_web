from django.db import models

class Freelancer(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('licenca', 'Licença'),
    ]

    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    contato = models.CharField(max_length=50)
    valor_hora = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ativo') 

    def __str__(self):
        return self.nome