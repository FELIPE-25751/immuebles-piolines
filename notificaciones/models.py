from django.db import models
from core.models import Usuario
from django.utils import timezone
from firebase_admin import firestore


class Notificacion(models.Model):
    """
    Modelo para el sistema de notificaciones
    """
    TIPO_CHOICES = [
        ('sistema', 'Sistema'),
        ('inmueble', 'Inmueble'),
        ('contrato', 'Contrato'),
        ('pago', 'Pago'),
        ('mantenimiento', 'Mantenimiento'),
        ('mensaje', 'Mensaje'),
    ]
    
    # Destinatario
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    
    # Contenido de la notificación
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='sistema')
    
    # Enlace opcional
    enlace = models.CharField(max_length=500, blank=True)
    
    # Estado
    leida = models.BooleanField(default=False)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Prioridad
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
    ]
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='normal')
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario', 'leida']),
            models.Index(fields=['-fecha_creacion']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"
    
    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save()
    
    def save_to_firebase(self):
        """Guarda la notificación en Firebase"""
        try:
            db = firestore.client()
            notif_ref = db.collection('notificaciones').document(str(self.id))
            notif_ref.set({
                'usuario_id': self.usuario.id,
                'titulo': self.titulo,
                'mensaje': self.mensaje,
                'tipo': self.tipo,
                'enlace': self.enlace,
                'leida': self.leida,
                'fecha_creacion': self.fecha_creacion.isoformat(),
                'prioridad': self.prioridad
            })
            return True
        except Exception as e:
            print(f"Error al guardar en Firebase: {e}")
            return False
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Guardar en Firebase después de guardar en DB
        self.save_to_firebase()


class ConfiguracionNotificaciones(models.Model):
    """
    Modelo para configuración de notificaciones del usuario
    """
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='config_notificaciones'
    )
    
    # Configuración de notificaciones por tipo
    notif_inmuebles = models.BooleanField(default=True)
    notif_contratos = models.BooleanField(default=True)
    notif_pagos = models.BooleanField(default=True)
    notif_mantenimientos = models.BooleanField(default=True)
    notif_mensajes = models.BooleanField(default=True)
    
    # Notificaciones por email
    email_inmuebles = models.BooleanField(default=False)
    email_contratos = models.BooleanField(default=True)
    email_pagos = models.BooleanField(default=True)
    email_mantenimientos = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Configuración de Notificaciones'
        verbose_name_plural = 'Configuraciones de Notificaciones'
    
    def __str__(self):
        return f"Configuración de {self.usuario.username}"
