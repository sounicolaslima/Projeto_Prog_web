from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    freelancer = models.OneToOneField('Freelancer', on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=[
        ('admin', 'Administrador'),
        ('freelancer', 'Freelancer')
    ], default='admin')

    def __str__(self):
        return f"{self.user.username} - {self.tipo}"

    def save(self, *args, **kwargs):
        # Se for do tipo freelancer e não tiver um freelancer associado, criar um automaticamente
        if self.tipo == 'freelancer' and not self.freelancer:
            # Criar um freelancer básico associado ao usuário
            freelancer = Freelancer.objects.create(
                nome=self.user.username,
                cpf=f"000.000.000-{self.user.id:02d}",  # CPF temporário
                contato=self.user.email or "",
                valor_hora=50.00,  # Valor padrão
                status='ativo'
            )
            self.freelancer = freelancer
        super().save(*args, **kwargs)

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

    @property
    def tipo_usuario(self):
        """Sempre retorna 'freelancer' ou 'admin' - nunca 'sem_perfil'"""
        try:
            perfil = PerfilUsuario.objects.get(freelancer=self)
            return perfil.tipo
        except PerfilUsuario.DoesNotExist:
            # Se não existe, criar um automaticamente como 'freelancer'
            from django.contrib.auth.models import User
            
            username = self.cpf.replace('.', '').replace('-', '')
            if User.objects.filter(username=username).exists():
                username = f"{username}_{User.objects.count() + 1}"
            
            user = User.objects.create_user(
                username=username,
                email=self.contato if '@' in self.contato else '',
                password='temp123'
            )
            
            perfil = PerfilUsuario.objects.create(
                user=user,
                freelancer=self,
                tipo='freelancer'  # Padrão como freelancer
            )
            return perfil.tipo