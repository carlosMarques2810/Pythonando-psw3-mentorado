from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import timedelta
import secrets 
from datetime import time

class Navigators(models.Model):
    nome = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome
    
    class Meta:
        db_table = 'navigators'
        verbose_name = 'navigators'
        verbose_name_plural = 'navigators'

class Estagios(models.TextChoices):
    E1 = 'E1', '10-100K'
    E2 = 'E2', '101-500K'
    E3 = 'E3', '501-1M'

class Mentorados(models.Model):
    nome = models.CharField(max_length=255)
    foto = models.ImageField(upload_to='fotos', null=True, blank=True)
    estagio = models.CharField(max_length=2, choices=Estagios.choices, default=Estagios.E1)
    navigator = models.ForeignKey(Navigators, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    criado_em = models.DateField(auto_now_add=True)
    token = models.CharField(max_length=16, null=True, blank=True)

    class Meta:
        db_table = 'mentorados'
        verbose_name = 'mentorados'
        verbose_name_plural = 'mentorados'
        
    def __str__(self):
        return self.nome
    
    def gerar_token_unico(self):
        while True:
            token = secrets.token_urlsafe(8)
            if not Mentorados.objects.filter(token=token).exists():
                return token

    def save(self, *args, **kwargs):
        # adição do token de autenticação
        if not self.token:
            self.token = self.gerar_token_unico()
        return super().save(*args, **kwargs)
    
# Reuniões
    
class DisponibilidadeHorarios(models.Model):
    data_inicial = models.DateTimeField(null=True, blank=True)
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    agendado = models.BooleanField(default=False)

    @property
    def data_final(self):
        return self.data_inicial + timedelta(minutes=50)
    
    class Meta:
        db_table = 'horarios'
        verbose_name = 'horarios'
        verbose_name_plural = 'horarios'
    
    def __str__(self):
        return f'{self.data_inicial.time()} às {self.data_final.time()}'

class Tag(models.TextChoices):
    G = 'G', 'Gestão'
    M = 'M', 'Marketing'
    RH = 'RH', 'Gestão de pessoas'
    I = 'I', 'Impostos'
    
class Reuniao(models.Model):
    data = models.ForeignKey(DisponibilidadeHorarios, on_delete=models.CASCADE)
    mentorado = models.ForeignKey(Mentorados, on_delete=models.CASCADE)
    tag = models.CharField(max_length=2, choices=Tag.choices, default=Tag.G)
    descricao = models.TextField()

    class Meta:
        db_table = 'reunioes'
        verbose_name = 'reunioes'
        verbose_name_plural = 'reunioes'

    def __str__(self):
        return f'{self.mentorado} - {self.data}'

class Tarefa(models.Model):
    mentorado = models.ForeignKey(Mentorados, on_delete=models.DO_NOTHING)
    tarefa = models.CharField(max_length=255)
    realizada = models.BooleanField(default=False)

    class Meta:
        db_table = 'tarefas'
        verbose_name = 'tarefa'
        verbose_name_plural = 'tarefas'

class Upload(models.Model):
    mentorado = models.ForeignKey(Mentorados, on_delete=models.DO_NOTHING)
    video = models.FileField(upload_to='video')

    class Meta:
        db_table = 'upload'
        verbose_name = 'upload'
        verbose_name_plural = 'uploads'