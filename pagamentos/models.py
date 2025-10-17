from django.db import models
from freelancers.models import Freelancer

class Pagamento(models.Model):
    STATUS_CHOICES = [
        ("Pendente", "Pendente"),
        ("Pago", "Pago")
    ]

    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE)
    periodo_inicio = models.DateField()
    periodo_fim = models.DateField()
    valor_calculado = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.freelancer.nome} - {self.periodo_inicio} a {self.periodo_fim}"

