from django.db import models
from contratos.models import Contrato
from django.utils import timezone
from firebase_admin import firestore


class Pago(models.Model):
    """
    Modelo para gestión de pagos de arriendo
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('vencido', 'Vencido'),
        ('parcial', 'Pago Parcial'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
        ('tarjeta', 'Tarjeta'),
        ('cheque', 'Cheque'),
        ('otro', 'Otro'),
    ]
    
    # Relaciones
    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.CASCADE,
        related_name='pagos'
    )
    
    # Información del pago
    numero_pago = models.CharField(max_length=50, unique=True, blank=True)
    concepto = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    
    # Montos
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    monto_pagado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mora = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Fechas
    periodo_inicio = models.DateField()
    periodo_fin = models.DateField()
    fecha_vencimiento = models.DateField()
    fecha_pago = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Estado y método
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, blank=True)
    
    # Comprobante
    comprobante = models.FileField(upload_to='comprobantes/', blank=True, null=True)
    referencia_pago = models.CharField(max_length=100, blank=True)
    
    # Cuenta de cobro
    cuenta_cobro_generada = models.BooleanField(default=False)
    fecha_generacion_cuenta = models.DateTimeField(null=True, blank=True)
    archivo_cuenta_cobro = models.FileField(upload_to='cuentas_cobro/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha_vencimiento']
    
    def __str__(self):
        return f"Pago #{self.numero_pago} - {self.concepto}"
    
    def save(self, *args, **kwargs):
        # Generar número de pago automáticamente
        if not self.numero_pago:
            ultimo = Pago.objects.order_by('-id').first()
            numero = 1 if not ultimo else ultimo.id + 1
            self.numero_pago = f"PAG-{timezone.now().year}-{numero:06d}"
        
        # Actualizar estado según monto pagado
        if self.monto_pagado >= self.monto + self.mora:
            self.estado = 'pagado'
        elif self.monto_pagado > 0:
            self.estado = 'parcial'
        elif self.fecha_vencimiento < timezone.now().date() and self.estado == 'pendiente':
            self.estado = 'vencido'
        
        super().save(*args, **kwargs)
    
    def get_monto_total(self):
        """Retorna el monto total incluyendo mora"""
        return self.monto + self.mora
    
    def get_saldo_pendiente(self):
        """Retorna el saldo pendiente por pagar"""
        return self.get_monto_total() - self.monto_pagado
    
    def esta_vencido(self):
        """Verifica si el pago está vencido"""
        return timezone.now().date() > self.fecha_vencimiento and self.estado != 'pagado'
    
    def dias_vencimiento(self):
        """Retorna los días de vencimiento"""
        if self.esta_vencido():
            delta = timezone.now().date() - self.fecha_vencimiento
            return delta.days
        return 0
    
    def calcular_mora(self, tasa_diaria=0.001):
        """Calcula la mora por días de vencimiento"""
        if self.esta_vencido():
            dias = self.dias_vencimiento()
            self.mora = float(self.monto) * tasa_diaria * dias
            self.save()
    
    def save_to_firebase(self):
        """Guarda el pago en Firebase"""
        try:
            db = firestore.client()
            pago_ref = db.collection('pagos').document(str(self.id))
            pago_ref.set({
                'numero_pago': self.numero_pago,
                'contrato_id': self.contrato.id,
                'concepto': self.concepto,
                'monto': float(self.monto),
                'monto_pagado': float(self.monto_pagado),
                'mora': float(self.mora),
                'estado': self.estado,
                'fecha_vencimiento': self.fecha_vencimiento.isoformat(),
                'fecha_pago': self.fecha_pago.isoformat() if self.fecha_pago else None,
                'metodo_pago': self.metodo_pago
            })
            return True
        except Exception as e:
            print(f"Error al guardar en Firebase: {e}")
            return False


class RegistroPago(models.Model):
    """
    Modelo para registrar los pagos realizados
    """
    pago = models.ForeignKey(
        Pago,
        on_delete=models.CASCADE,
        related_name='registros'
    )
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=20, choices=Pago.METODO_PAGO_CHOICES)
    referencia = models.CharField(max_length=100, blank=True)
    comprobante = models.FileField(upload_to='comprobantes/', blank=True)
    notas = models.TextField(blank=True)
    registrado_por = models.ForeignKey(
        'core.Usuario',
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        verbose_name = 'Registro de Pago'
        verbose_name_plural = 'Registros de Pagos'
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"Registro de {self.monto} para {self.pago.numero_pago}"
