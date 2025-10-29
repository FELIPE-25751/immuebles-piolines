from django.db import models
from core.models import Usuario
from firebase_admin import firestore
from django.utils import timezone


class Inmueble(models.Model):
    """
    Modelo para gestión de inmuebles
    """
    CATEGORIA_CHOICES = [
        ('casa', 'Casa'),
        ('apartamento', 'Apartamento'),
        ('local', 'Local Comercial'),
        ('oficina', 'Oficina'),
        ('bodega', 'Bodega'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('arrendado', 'Arrendado'),
        ('mantenimiento', 'En Mantenimiento'),
        ('no_disponible', 'No Disponible'),
    ]
    
    # Información básica
    propietario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='inmuebles_propietario'
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    
    # Ubicación
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    barrio = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10, blank=True)
    
    # Características
    area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Área en m²")
    habitaciones = models.IntegerField(default=0)
    banos = models.IntegerField(default=0)
    parqueaderos = models.IntegerField(default=0)
    piso = models.IntegerField(null=True, blank=True)
    
    # Económico
    precio_arriendo = models.DecimalField(max_digits=12, decimal_places=2)
    precio_administracion = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deposito_seguridad = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Características adicionales
    amoblado = models.BooleanField(default=False)
    mascotas_permitidas = models.BooleanField(default=False)
    
    # Servicios incluidos
    agua_incluida = models.BooleanField(default=False)
    luz_incluida = models.BooleanField(default=False)
    gas_incluida = models.BooleanField(default=False)
    internet_incluido = models.BooleanField(default=False)
    
    # Metadata
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Inmueble'
        verbose_name_plural = 'Inmuebles'
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.titulo} - {self.get_categoria_display()}"
    
    def get_precio_total(self):
        """Retorna el precio total incluyendo administración"""
        return self.precio_arriendo + self.precio_administracion
    
    def esta_disponible(self):
        """Verifica si el inmueble está disponible"""
        return self.estado == 'disponible' and self.activo
    
    def get_imagenes(self):
        """Retorna todas las imágenes del inmueble"""
        return self.imagenes.all()
    
    def get_imagen_principal(self):
        """Retorna la imagen principal del inmueble"""
        return self.imagenes.filter(principal=True).first() or self.imagenes.first()
    
    def save_to_firebase(self):
        """Guarda el inmueble en Firebase"""
        try:
            db = firestore.client()
            inmueble_ref = db.collection('inmuebles').document(str(self.id))
            inmueble_ref.set({
                'titulo': self.titulo,
                'descripcion': self.descripcion,
                'categoria': self.categoria,
                'estado': self.estado,
                'direccion': self.direccion,
                'ciudad': self.ciudad,
                'barrio': self.barrio,
                'area': float(self.area),
                'habitaciones': self.habitaciones,
                'banos': self.banos,
                'precio_arriendo': float(self.precio_arriendo),
                'precio_administracion': float(self.precio_administracion),
                'propietario_id': self.propietario.id,
                'fecha_registro': self.fecha_registro,
                'activo': self.activo
            })
            return True
        except Exception as e:
            print(f"Error al guardar en Firebase: {e}")
            return False


class ImagenInmueble(models.Model):
    """
    Modelo para las imágenes de los inmuebles
    """
    inmueble = models.ForeignKey(
        Inmueble,
        on_delete=models.CASCADE,
        related_name='imagenes'
    )
    imagen = models.ImageField(upload_to='inmuebles/')
    descripcion = models.CharField(max_length=200, blank=True)
    principal = models.BooleanField(default=False)
    orden = models.IntegerField(default=0)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Imagen de Inmueble'
        verbose_name_plural = 'Imágenes de Inmuebles'
        ordering = ['orden', '-principal']
    
    def __str__(self):
        return f"Imagen de {self.inmueble.titulo}"
    
    def save(self, *args, **kwargs):
        # Si se marca como principal, desmarcar las demás
        if self.principal:
            ImagenInmueble.objects.filter(
                inmueble=self.inmueble,
                principal=True
            ).update(principal=False)
        super().save(*args, **kwargs)


class CaracteristicaAdicional(models.Model):
    """
    Modelo para características adicionales de los inmuebles
    """
    inmueble = models.ForeignKey(
        Inmueble,
        on_delete=models.CASCADE,
        related_name='caracteristicas'
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, blank=True)  # Para FontAwesome o similar
    
    class Meta:
        verbose_name = 'Característica Adicional'
        verbose_name_plural = 'Características Adicionales'
    
    def __str__(self):
        return f"{self.nombre} - {self.inmueble.titulo}"
