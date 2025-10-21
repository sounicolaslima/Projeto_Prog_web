from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    freelancer = models.OneToOneField('Freelancer', on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=[
        ('admin', 'Administrador'),
        ('freelancer', 'Freelancer')
    ], default='admin')

    def __str__(self):
        return f"{self.user.username} - {self.tipo}"

@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)

@receiver(post_save, sender=User)
def salvar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, 'perfilusuario'):
        instance.perfilusuario.save()
    else:
        PerfilUsuario.objects.get_or_create(user=instance)
    
    