from django.db import models
from core.models import Usuario
from inmuebles.models import Inmueble
from django.utils import timezone

class SolicitudArriendo(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('cancelada', 'Cancelada'),
    ]
    inmueble = models.ForeignKey(Inmueble, on_delete=models.CASCADE, related_name='solicitudes_arriendo')
    inquilino = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitudes_realizadas')
    propietario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitudes_recibidas')
    mensaje = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_solicitud = models.DateTimeField(default=timezone.now)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Solicitud de Arriendo'
        verbose_name_plural = 'Solicitudes de Arriendo'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"Solicitud de {self.inquilino} para {self.inmueble}"