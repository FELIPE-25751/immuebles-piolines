from django.db import models
from core.models import Usuario
from inmuebles.models import Inmueble
from django.utils import timezone
from firebase_admin import firestore


class Mantenimiento(models.Model):
    """
    Modelo para gestión de solicitudes de mantenimiento
    """
    TIPO_CHOICES = [
        ('plomeria', 'Plomería'),
        ('electricidad', 'Electricidad'),
        ('pintura', 'Pintura'),
        ('cerrajeria', 'Cerrajería'),
        ('limpieza', 'Limpieza'),
        ('electrodomestico', 'Electrodomésticos'),
        ('estructura', 'Estructura'),
        ('otro', 'Otro'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_revision', 'En Revisión'),
        ('aprobado', 'Aprobado'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
        ('rechazado', 'Rechazado'),
    ]
    
    # Relaciones
    inmueble = models.ForeignKey(
        Inmueble,
        on_delete=models.CASCADE,
        related_name='mantenimientos'
    )
    solicitante = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='mantenimientos_solicitados'
    )
    asignado_a = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenimientos_asignados'
    )
    
    # Información del mantenimiento
    numero_ticket = models.CharField(max_length=50, unique=True, blank=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='media')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    # Ubicación específica en el inmueble
    ubicacion_especifica = models.CharField(max_length=200, blank=True, 
                                           help_text='Ej: Cocina, Baño principal, etc.')
    
    # Fechas
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    fecha_estimada = models.DateField(null=True, blank=True)
    
    # Costos
    costo_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_final = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Responsable del costo
    RESPONSABLE_CHOICES = [
        ('propietario', 'Propietario'),
        ('inquilino', 'Inquilino'),
        ('compartido', 'Compartido'),
    ]
    responsable_costo = models.CharField(
        max_length=20,
        choices=RESPONSABLE_CHOICES,
        default='propietario'
    )
    
    # Notas y seguimiento
    notas_propietario = models.TextField(blank=True)
    solucion_aplicada = models.TextField(blank=True)
    
    # Archivos
    imagen = models.ImageField(upload_to='mantenimientos/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Mantenimiento'
        verbose_name_plural = 'Mantenimientos'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"{self.numero_ticket} - {self.titulo}"
    
    def save(self, *args, **kwargs):
        # Generar número de ticket automáticamente
        if not self.numero_ticket:
            ultimo = Mantenimiento.objects.order_by('-id').first()
            numero = 1 if not ultimo else ultimo.id + 1
            self.numero_ticket = f"MNT-{timezone.now().year}-{numero:05d}"
        
        super().save(*args, **kwargs)
    
    def esta_activo(self):
        """Verifica si el mantenimiento está activo"""
        return self.estado in ['pendiente', 'en_revision', 'aprobado', 'en_proceso']
    
    def dias_desde_solicitud(self):
        """Retorna los días desde la solicitud"""
        delta = timezone.now() - self.fecha_solicitud
        return delta.days
    
    def save_to_firebase(self):
        """Guarda el mantenimiento en Firebase"""
        try:
            db = firestore.client()
            mant_ref = db.collection('mantenimientos').document(str(self.id))
            mant_ref.set({
                'numero_ticket': self.numero_ticket,
                'inmueble_id': self.inmueble.id,
                'solicitante_id': self.solicitante.id,
                'titulo': self.titulo,
                'descripcion': self.descripcion,
                'tipo': self.tipo,
                'prioridad': self.prioridad,
                'estado': self.estado,
                'fecha_solicitud': self.fecha_solicitud.isoformat(),
                'costo_estimado': float(self.costo_estimado),
                'responsable_costo': self.responsable_costo
            })
            return True
        except Exception as e:
            print(f"Error al guardar en Firebase: {e}")
            return False


class SeguimientoMantenimiento(models.Model):
    """
    Modelo para el seguimiento de mantenimientos
    """
    mantenimiento = models.ForeignKey(
        Mantenimiento,
        on_delete=models.CASCADE,
        related_name='seguimientos'
    )
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    archivo_adjunto = models.FileField(upload_to='seguimientos/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Seguimiento de Mantenimiento'
        verbose_name_plural = 'Seguimientos de Mantenimientos'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Seguimiento de {self.mantenimiento.numero_ticket} por {self.usuario.username}"
