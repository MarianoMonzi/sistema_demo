from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.dispatch import receiver

# Create your models here.


class Cliente(models.Model):
    nombre = models.CharField(max_length=50)
    numero = models.BigIntegerField()
    patente = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.nombre


class MensajeWhatsApp(models.Model):
    cliente_id = models.IntegerField()
    enviar_mensaje = models.BooleanField(default=False)
    fecha_envio = models.DateField(null=True, blank=True)
    tarea_id = models.IntegerField(null=True, blank=True)
    enviado = models.BooleanField(default=False)

    def marcar_como_enviado(self):
        self.enviado = True
        self.save()

    def __str__(self):
        return f"Cliente ID: {self.cliente_id}, Enviar mensaje: {self.enviar_mensaje}, Fecha envío: {self.fecha_envio}"


class Planillas(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    # Puede ser 'correctiva' o 'preventiva'
    lista_tipo = models.CharField(max_length=20)

    def __str__(self):
        return f'Planilla {self.id} - Cliente: {self.cliente.nombre}'


class PlanillaCliente(models.Model):
    planillaId = models.ForeignKey(Planillas, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    cambio = models.BooleanField(default=False)
    checkbox = models.BooleanField(default=False)
    observaciones = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.nombre


class Tarea(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateField(default=datetime.today)
    planilla = models.ForeignKey(
        Planillas, on_delete=models.CASCADE, null=True, blank=True)
    kilometros = models.IntegerField()
    proxservicio = models.DateField()
    mecanico = models.ForeignKey(User, on_delete=models.CASCADE)


class ListaCorrectiva(models.Model):
    items = models.CharField(max_length=255)


class ListaPreventiva(models.Model):
    items = models.CharField(max_length=255)
