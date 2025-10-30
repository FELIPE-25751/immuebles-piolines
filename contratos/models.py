from django.db import models
from core.models import Usuario
from .models_solicitud import SolicitudArriendo
from inmuebles.models import Inmueble
from django.utils import timezone
from datetime import timedelta
from firebase_admin import firestore


class Contrato(models.Model):
    """
    Modelo para gestión de contratos de arrendamiento
    """
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('pendiente_firma', 'Pendiente de Firma'),
        ('activo', 'Activo'),
        ('vencido', 'Vencido'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    
    # Partes del contrato
    inmueble = models.ForeignKey(
        Inmueble,
        on_delete=models.CASCADE,
        related_name='contratos'
    )
    inquilino = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='contratos_inquilino'
    )
    
    # Información del contrato
    numero_contrato = models.CharField(max_length=50, unique=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    
    # Fechas
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Condiciones económicas
    valor_arriendo = models.DecimalField(max_digits=12, decimal_places=2)
    valor_administracion = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_deposito = models.DecimalField(max_digits=12, decimal_places=2)
    dia_pago = models.IntegerField(default=5, help_text="Día del mes para pago")
    
    # Firma digital
    firma_propietario = models.TextField(blank=True, help_text="Firma digital del propietario")
    fecha_firma_propietario = models.DateTimeField(null=True, blank=True)
    firma_inquilino = models.TextField(blank=True, help_text="Firma digital del inquilino")
    fecha_firma_inquilino = models.DateTimeField(null=True, blank=True)
    
    # Términos y condiciones
    terminos_condiciones = models.TextField()
    clausulas_especiales = models.TextField(blank=True)
    
    # Documentos
    documento_contrato = models.FileField(upload_to='contratos/', blank=True, null=True)
    
    # Metadata
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Contrato #{self.numero_contrato} - {self.inmueble.titulo}"
    
    def save(self, *args, **kwargs):
        # Generar número de contrato automáticamente
        if not self.numero_contrato:
            ultimo = Contrato.objects.order_by('-id').first()
            numero = 1 if not ultimo else ultimo.id + 1
            self.numero_contrato = f"CTR-{timezone.now().year}-{numero:05d}"
        
        super().save(*args, **kwargs)
        
        # Actualizar estado del inmueble si el contrato está activo
        if self.estado == 'activo':
            self.inmueble.estado = 'arrendado'
            self.inmueble.save()
        elif self.estado in ['finalizado', 'cancelado']:
            # Verificar si hay otros contratos activos
            otros_activos = Contrato.objects.filter(
                inmueble=self.inmueble,
                estado='activo'
            ).exclude(id=self.id).exists()
            
            if not otros_activos:
                self.inmueble.estado = 'disponible'
                self.inmueble.save()
    
    def get_duracion_meses(self):
        """Retorna la duración del contrato en meses"""
        delta = self.fecha_fin - self.fecha_inicio
        return delta.days // 30
    
    def get_valor_total_mensual(self):
        """Retorna el valor total mensual incluyendo administración"""
        return self.valor_arriendo + self.valor_administracion
    
    def esta_vigente(self):
        """Verifica si el contrato está vigente"""
        hoy = timezone.now().date()
        return self.fecha_inicio <= hoy <= self.fecha_fin and self.estado == 'activo'
    
    def dias_para_vencer(self):
        """Retorna los días que faltan para que venza el contrato"""
        if self.estado == 'activo':
            delta = self.fecha_fin - timezone.now().date()
            return delta.days
        return None
    
    def requiere_firma(self, usuario):
        """Verifica si un usuario necesita firmar el contrato"""
        if usuario == self.inmueble.propietario and not self.firma_propietario:
            return True
        if usuario == self.inquilino and not self.firma_inquilino:
            return True
        return False
    
    def esta_firmado_completo(self):
        """Verifica si el contrato está firmado por ambas partes"""
        return bool(self.firma_propietario and self.firma_inquilino)
    
    def save_to_firebase(self):
        """Guarda el contrato en Firebase"""
        try:
            db = firestore.client()
            contrato_ref = db.collection('contratos').document(str(self.id))
            contrato_ref.set({
                'numero_contrato': self.numero_contrato,
                'inmueble_id': self.inmueble.id,
                'inquilino_id': self.inquilino.id,
                'propietario_id': self.inmueble.propietario.id,
                'estado': self.estado,
                'fecha_inicio': self.fecha_inicio.isoformat(),
                'fecha_fin': self.fecha_fin.isoformat(),
                'valor_arriendo': float(self.valor_arriendo),
                'valor_administracion': float(self.valor_administracion),
                'valor_deposito': float(self.valor_deposito),
                'fecha_creacion': self.fecha_creacion.isoformat(),
                'firmado_completo': self.esta_firmado_completo()
            })
            return True
        except Exception as e:
            print(f"Error al guardar en Firebase: {e}")
            return False


class FirmaDigital(models.Model):
    """
    Modelo para almacenar las firmas digitales
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    firma_base64 = models.TextField(help_text="Firma en formato base64")
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    fecha_firma = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Firma Digital'
        verbose_name_plural = 'Firmas Digitales'
    
    def __str__(self):
        return f"Firma de {self.usuario.username} - {self.fecha_firma}"
